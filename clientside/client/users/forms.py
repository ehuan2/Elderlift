from flask_wtf import FlaskForm # the super class of flaskform
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField # different types of fields
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError # validators already in place
from client.main.utils import send_http_request # we need this to validate the email

import urllib.parse, json # helps with converting strings to http requests

class RegistrationForm(FlaskForm): # type of flask form

    # needs a name, email, password, confirm password, location, and contact, and role, and submit
    name = StringField('Name')
    email = StringField('Email', validators = [Email()])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password', validators = [EqualTo('password')])

    address = StringField('Address (can put your local grocer)')
    city = StringField('City')
    country = StringField('Country')

    contact = TextAreaField('Contact Information')
    role = RadioField('Choose your role!', choices = [('Elderly', 'Elderly'), ('Taskdoer', 'Taskdoer')])

    submit = SubmitField('Sign Up!')

    def validate_name(self, name): # validates the name as not being blank
        
        if not name.data:
            raise ValidationError("Cannot be left blank!")

    def validate_email(self, email):
        
        if not email.data:
            raise ValidationError("Cannot be left blank!")

        email_data = urllib.parse.quote(email.data) # gets the email in terms of http request form
        
        response = send_http_request(url = f"https://elderlift-serverside.ue.r.appspot.com/v1/api/user/{email_data}", method='GET', body={})

        if json.loads(response.content):
            raise ValidationError("That email is already taken!")

    def validate_password(self, password): # a check to make sure the password is good

        password_data = password.data # gets the data

        if password_data.isalpha(): # makes sure that it is long, and has a mix of characters and numbers
            raise ValidationError("You need numbers!")
        
        if password_data.isalnum():
            raise ValidationError("You need other symbols!")

        if len(password_data) < 8:
            raise ValidationError("You need at least 8 characters!")

    def validate_confirm_password(self, confirm_password): # confirm password validation
        if not confirm_password.data:
            raise ValidationError("Cannot be left blank!")

    def validate_address(self, address): # address validation
        if not address.data:
            raise ValidationError("Cannot be left blank!")

    def validate_city(self, city): # validates the city
        if not city.data:
            raise ValidationError("Cannot be left blank!")

    def validate_country(self, country): # validates the country
        if not country.data:
            raise ValidationError("Cannot be left blank!")

    def validate_role(self, role):
        
        if not role.data:
            raise ValidationError("You have to choose a role!")


class TokenForm(FlaskForm):
    token = StringField('Enter Token:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ResetPasswordForm(FlaskForm):

    email = StringField('Email', validators = [Email()])

    submit = SubmitField('Request Token')

    def validate_email(self, email):
        
        if not email.data:
            raise ValidationError("Cannot be left blank!")

        email_data = urllib.parse.quote(email.data) # gets the email in terms of http request form
        
        response = send_http_request(url = f"https://elderlift-serverside.ue.r.appspot.com/v1/api/user/{email_data}", method='GET', body={})

        if not json.loads(response.content):
            raise ValidationError("You don't have an account with that email! Sign up!")

 
class ResetPasswordTokenForm(FlaskForm):

    token = StringField('Token', validators = [DataRequired()])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password', validators = [EqualTo('password')])

    submit = SubmitField('Reset Password')

    def validate_password(self, password): # a check to make sure the password is good

        password_data = password.data # gets the data

        if password_data.isalpha(): # makes sure that it is long, and has a mix of characters and numbers
            raise ValidationError("You need numbers!")
        
        if password_data.isalnum():
            raise ValidationError("You need other symbols!")

        if len(password_data) < 8:
            raise ValidationError("You need at least 8 characters!")

    def validate_confirm_password(self, confirm_password): # confirm password validation
        if not confirm_password.data:
            raise ValidationError("Cannot be left blank!")


class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])

    submit = SubmitField("Enter")


class AccountForm(FlaskForm):
    name = StringField('Name')

    address = StringField('Address (can put your local grocer)')
    city = StringField('City')
    country = StringField('Country')

    contact = TextAreaField('Contact Information')

    submit = SubmitField('Update')

    def validate_name(self, name): # validates the name as not being blank
        
        if not name.data:
            raise ValidationError("Cannot be left blank!")

    def validate_address(self, address): # address validation
        if not address.data:
            raise ValidationError("Cannot be left blank!")

    def validate_city(self, city): # validates the city
        if not city.data:
            raise ValidationError("Cannot be left blank!")

    def validate_country(self, country): # validates the country
        if not country.data:
            raise ValidationError("Cannot be left blank!")