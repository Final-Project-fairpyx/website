from flask import Flask, render_template, request, redirect, url_for
# from fairpyx_integration import run_algorithm

app = Flask(__name__)

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
        for i in range(num_students):
            student_name = request.form[f'student_name_{i}']
            num_courses_student = int(request.form[f'student_courses_{i}'])
            students.append({'name': student_name, 'num_courses': num_courses_student})

        for i in range(num_courses):
            course_name = request.form[f'course_name_{i}']
            course_places = int(request.form[f'course_places_{i}'])
            courses.append({'name': course_name, 'places': course_places})

        return redirect(url_for('bids', num_students=num_students, num_courses=num_courses, students=students, courses=courses))

    return render_template('input.html', num_students=num_students, num_courses=num_courses)

# Route to input bids for courses
@app.route('/bids', methods=['GET', 'POST'])
def bids():
    if request.method == 'POST':
        bids = []
        students = request.form.getlist('students')
        courses = request.form.getlist('courses')
        for student in students:
            student_bids = {}
            for course in courses:
                bid = int(request.form[f'bid_{student}_{course}'])
                student_bids[course] = bid
            bids.append({'student': student, 'bids': student_bids})

        algo = request.form['algorithm']
        results = None  # Call your fairpyx algorithm here
        return render_template('results.html', results=results)

    students = request.args.getlist('students')
    courses = request.args.getlist('courses')
    return render_template('bids.html', students=students, courses=courses)

# Route to display results
@app.route('/results', methods=['GET'])
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True)
