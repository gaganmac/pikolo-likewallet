from flask_wtf import Form # , RecaptchaField

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import TextField, PasswordField, validators # BooleanField

# Import Form validators
from wtforms.validators import Required, Email, EqualTo


# Define the login form (WTForms)

class LoginForm(Form):
    email    = TextField('Email Address', [Email(),
                Required(message='Forgot your email address?')])
    password = PasswordField('Password', [
                Required(message='Must provide a password.')])



class RegistrationForm(Form):
	first = TextField('First Name', [validators.DataRequired()])
	last = TextField('Last Name', [validators.DataRequired()])
	company = TextField('Company Name', [validators.DataRequired()])
	website = TextField('Website Name', [validators.DataRequired()])
	email = TextField('Email Address', [Email(),
                Required(message='Forgot your email address?')])
	phone = TextField('Phone', [validators.DataRequired()])
	password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
	confirm = PasswordField('Repeat Password')

class RemoveForm(Form):
    email    = TextField('Email Address', [Email(),
                Required(message='Please enter the email address associated with your account')])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

