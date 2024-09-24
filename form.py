from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import ValidationError, DataRequired

class RegistrationForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    skill = SelectField(label='Skill', choices=[('Never surfed'),('Beginner'),('Intermediate'),('Expert'),('Professional')],validators=[DataRequired()])
    submit = SubmitField('Send')