import json
import logging
from flask import Flask, render_template, request, redirect, url_for, session
import fairpyx
import os
from fairpyx.explanations import StringsExplanationLogger
import cvxpy as cp

global call_algo

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

solver_mapping = {
    'cp.CBC': cp.CBC,
    'cp.MOSEK': cp.MOSEK,
    'cp.SCIP': cp.SCIP,
    'cp.GLPK_MI': cp.GLPK_MI,
    'cp.SCIPY': cp.SCIPY,
}

# Home route to choose the number of students and courses
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/demo', methods=['GET', 'POST'])
def demo():
    if request.method == 'POST':
        num_students = int(request.form['num_students'])
        num_courses = int(request.form['num_courses'])
        return redirect(url_for('input_details', num_students=num_students, num_courses=num_courses))
    return render_template('demo.html')


# Route to input student and course details
@app.route('/input/<int:num_students>/<int:num_courses>', methods=['GET', 'POST'])
def input_details(num_students, num_courses):
    if request.method == 'POST':
        students = []
        courses = []

        # Extract student details
        for i in range(num_students):
            student_name = request.form[f'student_name_{i}']
            num_courses_student = int(request.form[f'student_courses_{i}'])
            students.append({'name': student_name, 'num_courses': num_courses_student})

        # Extract course details
        for i in range(num_courses):
            course_name = request.form[f'course_name_{i}']
            course_places = int(request.form[f'course_places_{i}'])
            courses.append({'name': course_name, 'places': course_places})

        # Store data in session
        session['students'] = students
        session['courses'] = courses

        return redirect(url_for('bids'))

    return render_template('input.html', num_students=num_students, num_courses=num_courses)


# Route to input bids for courses
@app.route('/bids', methods=['GET', 'POST'])
def bids():

    global call_algo
    if request.method == 'POST':
        bids = []
        students = session.get('students', [])
        courses = session.get('courses', [])

        for student in students:
            student_bids = {}
            for course in courses:
                bid = int(request.form[f'bid_{student["name"]}_{course["name"]}'])
                student_bids[course["name"]] = bid
            bids.append({'student': student['name'], 'bids': student_bids})

        algo = request.form['algorithm']
        solver = request.form['cp_solver']

        # Deserialize the item conflicts from the form
        item_conflicts = request.form.get('item_conflicts', '{}')
        app.logger.debug("item_conflicts: ")
        app.logger.debug(item_conflicts)
        if item_conflicts:
            try:
                item_conflicts = json.loads(item_conflicts)  # Convert JSON string to Python dict
            except json.JSONDecodeError as e:
                app.logger.error(f"Failed to decode JSON: {e}")
                item_conflicts = {}  # Default to an empty dictionary if JSON decoding fails
        else:
            item_conflicts = {}  # Default to an empty dictionary if item_conflicts is None or empty

        app.logger.debug("Conflicts:")
        app.logger.debug(item_conflicts)

        # Prepare data for the algorithm
        agent_capacities = {student['name']: student['num_courses'] for student in students}
        item_capacities = {course['name']: course['places'] for course in courses}
        valuations = {student['name']: student_bids for student, student_bids in
                      zip(students, [b['bids'] for b in bids])}

        if item_conflicts != {}:
            app.logger.debug("instance with Conflicts")
            # Create instance with item conflicts
            instance = fairpyx.Instance(
                agent_capacities=agent_capacities,
                item_capacities=item_capacities,
                valuations=valuations,
                item_conflicts=item_conflicts  # Add the item conflicts to the instance
            )
        else:
            app.logger.debug("-instance without Conflicts")
            instance = fairpyx.Instance(
                agent_capacities=agent_capacities,
                item_capacities=item_capacities,
                valuations=valuations
            )

        app.logger.debug("agent_capacities:")
        app.logger.debug(agent_capacities)
        app.logger.debug("item_capacities:")
        app.logger.debug(item_capacities)
        app.logger.debug("valuations:")
        app.logger.debug(valuations)
        app.logger.debug("num of students:")
        app.logger.debug(len(students))
        app.logger.debug("solver:")
        app.logger.debug(solver)

        string_explanation_logger = StringsExplanationLogger([student['name'] for student in students], level=logging.INFO)

        solver_issue = False  # Initialize the flag
        # Call the fairpyx algorithm
        try:
            if algo == 'TTC':
                call_algo = fairpyx.algorithms.TTC_function
                results = fairpyx.divide(call_algo, instance=instance,
                                         explanation_logger=string_explanation_logger)
            elif algo == 'SP':
                call_algo = fairpyx.algorithms.SP_function
                results = fairpyx.divide(call_algo, instance=instance,
                                         explanation_logger=string_explanation_logger)
            elif algo == 'TTC-O':
                call_algo = fairpyx.algorithms.TTC_O_function
                # Attempt to use the selected solver
                solver = solver_mapping[solver]  # This will raise a KeyError if the solver is not found
                results = fairpyx.divide(call_algo, instance=instance, solver=solver,
                                         explanation_logger=string_explanation_logger)
            elif algo == 'SP-O':
                call_algo = fairpyx.algorithms.SP_O_function
                solver = solver_mapping[solver]
                results = fairpyx.divide(call_algo, instance=instance, solver=solver,
                                         explanation_logger=string_explanation_logger)
            elif algo == 'OC':
                call_algo = fairpyx.algorithms.OC_function
                solver = solver_mapping[solver]
                results = fairpyx.divide(call_algo, instance=instance, solver=solver,
                                         explanation_logger=string_explanation_logger)
            else:
                results = "Algorithm not recognized."
        except Exception as e:
            # Handle any other exceptions, including solver-specific issues
            app.logger.error(f"An unexpected error occurred: {e}. Attempting to run without a specific solver.")
            try:
                solver_issue = True  # Set the flag to True if a fallback occurs
                app.logger.debug("ENTER TO TRY")
                app.logger.debug("solver:")
                app.logger.debug(solver)
                string_explanation_logger = StringsExplanationLogger([student['name'] for student in students],
                                                                     level=logging.INFO)
                if solver == 'cp.MOSEK':
                    results = fairpyx.divide(call_algo, instance=instance, explanation_logger=string_explanation_logger,
                                             solver=cp.CBC)
                    solver = 'cp.CBC'
                else:
                    results = fairpyx.divide(call_algo, instance=instance, explanation_logger=string_explanation_logger, solver=None)

            except Exception as e:
                app.logger.error(f"An unexpected error occurred: {e}")
                results = f"An unexpected error occurred: {e}"

        # Continue with processing the results
        app.logger.debug("Algorithm Results:")
        app.logger.debug(results)
        app.logger.debug("Debug Results:")
        app.logger.debug(string_explanation_logger.map_agent_to_explanation())

        # Parse the explanation logger's output into a more structured format
        courses = session.get('courses', [])
        course_mapping = {course['name'] for course in courses}  # Assuming course names are unique and used as identifiers

        # Parse the explanation logger's output into a more structured format
        parsed_results = {
            student: {
                "courses": [],
                "details": ""
            }
            for student in string_explanation_logger.map_agent_to_explanation().keys()
        }

        for student, explanation in string_explanation_logger.map_agent_to_explanation().items():
            allocated_courses = []
            lines = explanation.splitlines()
            for line in lines:
                if "you get course" in line:
                    if algo == "SP":
                        course_code = line.split(" ")[3]
                    else:
                        course_code = line.split(" ")[-4]  # Extract the course identifier (e.g., C1, C2)
                    allocated_courses.append(course_code)  # Append course name instead of code
            parsed_results[student]["courses"] = allocated_courses
            parsed_results[student]["details"] = explanation

        # Consolidate conflicts
        consolidated_conflicts = {}
        for course, conflict_list in item_conflicts.items():
            if course not in consolidated_conflicts:
                consolidated_conflicts[course] = set(conflict_list)  # Use a set to avoid duplicates
            else:
                consolidated_conflicts[course].update(conflict_list)

        # Convert to a list of dictionaries for easier rendering
        formatted_conflicts = [{'course': course, 'conflict': ', '.join(sorted(conflicts))} for course, conflicts in
                               consolidated_conflicts.items()]

        # Prepare input data for the result page
        input_data = {
            'num_students': len(students),
            'num_courses': len(courses),
            'students': [{'name': student['name'], 'num_courses': student['num_courses']} for student in students],
            'courses': [{'name': course['name'], 'places': course['places']} for course in courses],
            'bids': {student['name']: student_bids for student, student_bids in
                     zip(students, [b['bids'] for b in bids])},
            'algorithm': algo,
            'solver': solver if not solver_issue else 'Not Used a Specific Solver',
            'conflicts': formatted_conflicts if formatted_conflicts else []
        }

        # Pass the parsed results and input data to the result page
        return render_template("result.html", results=parsed_results, solver_issue=solver_issue,
                               input_data=input_data)

    students = session.get('students', [])
    courses = session.get('courses', [])
    num_courses = len(courses)  # Get the number of courses

    return render_template('bids.html', students=students, courses=courses, num_courses=num_courses)


# Route to display results
@app.route('/result', methods=['GET', 'POST'])
def results():
    return render_template('result.html')


if __name__ == '__main__':
    app.run(port=5005,debug=True)