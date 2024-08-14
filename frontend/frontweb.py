from flask import Flask, render_template, request, redirect, url_for, session
import fairpyx
import os


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

        # Create instance
        instance = fairpyx.Instance(
            agent_capacities=agent_capacities,
            item_capacities=item_capacities,
            valuations=valuations
        )

        # Call the fairpyx algorithm
        if algo == 'TTC':
            results = fairpyx.divide(fairpyx.algorithms.TTC_function, instance=instance)
        elif algo == 'SP':
            results = fairpyx.divide(fairpyx.algorithms.SP_function, instance=instance)
        # Add other algorithm cases here if needed
        else:
            results = "Algorithm not recognized."

        # Use logging to print results
        app.logger.debug("Algorithm Results:")
        app.logger.debug(results)

        return render_template('results.html', results=results)
    students = session.get('students', [])
    courses = session.get('courses', [])

    return render_template('bids.html', students=students, courses=courses)


# Route to display results
@app.route('/result', methods=['GET', 'POST'])
def results():
    return render_template('result.html')


if __name__ == '__main__':
    app.run(debug=True)
