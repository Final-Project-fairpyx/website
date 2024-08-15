import logging
from flask import Flask, render_template, request, redirect, url_for, session
import fairpyx
import os
from fairpyx.explanations import StringsExplanationLogger


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management


# Home route to choose the number of students and courses
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num_students = int(request.form['num_students'])
        num_courses = int(request.form['num_courses'])
        return redirect(url_for('input_details', num_students=num_students, num_courses=num_courses))
    return render_template('index.html')


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

        # Prepare data for the algorithm
        agent_capacities = {student['name']: student['num_courses'] for student in students}
        item_capacities = {course['name']: course['places'] for course in courses}
        valuations = {student['name']: student_bids for student, student_bids in
                      zip(students, [b['bids'] for b in bids])}

        app.logger.debug("agent_capacities:")
        app.logger.debug(agent_capacities)
        app.logger.debug("item_capacities:")
        app.logger.debug(item_capacities)
        app.logger.debug("valuations:")
        app.logger.debug(valuations)
        app.logger.debug("num of students:")
        app.logger.debug(len(students))

        # Create instance
        instance = fairpyx.Instance(
            agent_capacities=agent_capacities,
            item_capacities=item_capacities,
            valuations=valuations
        )

        string_explanation_logger = StringsExplanationLogger([student['name'] for student in students], level=logging.INFO)



        # Call the fairpyx algorithm
        if algo == 'TTC':
            results = fairpyx.divide(fairpyx.algorithms.TTC_function, instance=instance, explanation_logger=string_explanation_logger)
        elif algo == 'SP':
            results = fairpyx.divide(fairpyx.algorithms.SP_function, instance=instance, explanation_logger=string_explanation_logger)
        elif algo == 'TTC-O':
            results = fairpyx.divide(fairpyx.algorithms.TTC_O_function, instance=instance, solver=solver, explanation_logger=string_explanation_logger)
        elif algo == 'SP-O':
            results = fairpyx.divide(fairpyx.algorithms.SP_O_function, instance=instance, solver=solver, explanation_logger=string_explanation_logger)
        elif algo == 'OC':
            results = fairpyx.divide(fairpyx.algorithms.OC_function, instance=instance, solver=solver, explanation_logger=string_explanation_logger)
        # Add other algorithm cases here if needed
        else:
            results = "Algorithm not recognized."

        # Use logging to print results
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
                    course_code = line.split(" ")[-4]  # Extract the course identifier (e.g., C1, C2)
                    # course_name = course_mapping.get(course_code, course_code)  # Get course name from the mapping
                    allocated_courses.append(course_code)  # Append course name instead of code
            parsed_results[student]["courses"] = allocated_courses
            parsed_results[student]["details"] = explanation

        # Pass the parsed results to the result page
        return render_template("result.html", results=parsed_results)

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
