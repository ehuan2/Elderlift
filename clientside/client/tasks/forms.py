from flask_wtf import FlaskForm # the super class of flaskform
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField # different types of fields
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError # validators already in place

class TaskForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired()])
    content = TextAreaField('Description', validators = [DataRequired()])

    submit = SubmitField("Create Task")