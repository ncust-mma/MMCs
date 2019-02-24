# -*- coding: utf-8 -*-

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (BooleanField, PasswordField, RadioField, StringField,
                     SubmitField, TextAreaField, ValidationError)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

from MMCs.models import User


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(1, 30)])
    password = PasswordField('Password', validators=[DataRequired()])
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
    remark = TextAreaField('Remark')
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField()

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')


class EditProfileForm(FlaskForm):
    username = StringField(
        'Username', validators=[
            DataRequired(), Length(1, 30),
            Regexp('^[a-zA-Z0-9]*$', message='The username should contain only a-z, A-Z and 0-9.')]
    )
    realname = StringField('Realname',
                           validators=[DataRequired(), Length(1, 30)])
    remark = TextAreaField('Remark')
    submit = SubmitField()

    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField(
        'New Password', validators=[DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField()
