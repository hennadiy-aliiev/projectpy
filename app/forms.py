from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, Length


class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=18)])


class SignUpForm(FlaskForm):
    email = StringField('New email', validators=[DataRequired(), Email()])
    password = PasswordField('New password', validators=[
        DataRequired(), Length(min=6, max=18), EqualTo('confirm', message='Passwords must match')
        ])
    confirm = PasswordField('Confirm password')


class EmailForm(FlaskForm):                                                
    email = StringField('Email', validators=[DataRequired(), Email()])


class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=18)])


class EditForm(FlaskForm):
    nickname = StringField('nickname', validators=[Length(min=5, max=20)])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])


class PostForm(FlaskForm):
    post = StringField('post', validators=[DataRequired()])


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])
