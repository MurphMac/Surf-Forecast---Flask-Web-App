from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import ValidationError, DataRequired

#Form including fields for user's account
class RegistrationForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    skill = SelectField(label='Skill', choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')], validators=[DataRequired()])
    favourite_location = SelectField(label='Favourite Location', choices=[('Tauranga', 'Tauranga'), ('Gisborne', 'Gisborne'), ('Dunedin', 'Dunedin'), ('Christchurch', 'Christchurch')], validators=[DataRequired()])
    submit = SubmitField('Send')