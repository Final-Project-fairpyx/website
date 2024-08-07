from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired

class InputForm(FlaskForm):
    students = IntegerField('Number of Students', validators=[DataRequired()])
    courses = IntegerField('Number of Courses', validators=[DataRequired()])
    generate_random_students = BooleanField('Generate Random Students')
    generate_random_courses = BooleanField('Generate Random Courses')
    generate_random_bids = BooleanField('Generate Random Bids')
    algorithm = SelectField('Algorithm', choices=[('TTC', 'TTC'), ('SP', 'SP'), ('TTC-O', 'TTC-O'), ('SP-O', 'SP-O'), ('OC', 'OC')])
    submit = SubmitField('Submit')
