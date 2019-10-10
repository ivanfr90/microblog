from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from werkzeug.routing import ValidationError
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

from .models import User


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Log In'))


class SignInForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Confirm Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Sign In'))

    def validate_username(username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(_l('Username already exists'))

    def validate_email(email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(_l('Email already registered.'))


class ResetPasswordForm(FlaskForm):
    email = StringField(_l('Your email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Restore'))


class UpdatePasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Confirm Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Update'))
