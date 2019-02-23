# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import (BooleanField, PasswordField, RadioField, StringField,
                     SubmitField, TextField, ValidationError)
from wtforms.validators import DataRequired, EqualTo, Length, Regexp

from MMCs.models import User


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(1, 30)])
    password = PasswordField('Password', DataRequired())
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class RegisterForm(FlaskForm):
    username = StringField(
        'Username', validators=[
            DataRequired(), Length(1, 30),
            Regexp('^[a-zA-Z0-9]*$', message='The username should contain only a-z, A-Z and 0-9.')]
    )
    realname = StringField('Realname',
                           validators=[DataRequired(), Length(1, 30)])
    permission = RadioField(
        'Permission',
        choices=[('Teacher', 'As teacher user'),
                 ('Admin', 'As administrator user'),
                 ('Root', 'As root user')]
    )
    remark = TextField('Remark')
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField()

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField()


class TeacherUpdateInfoForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField()


class AdminUpdateInfoForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField()


class TeacherUpdateInfoForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField()


class UpdateInfoForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField()
