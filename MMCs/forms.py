# -*- coding: utf-8 -*-

from flask_ckeditor import CKEditorField
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (BooleanField, PasswordField, RadioField, StringField,
                     SubmitField, TextAreaField, ValidationError)
from wtforms.validators import DataRequired, EqualTo, Length, Regexp

from MMCs.models import UploadFileType, User


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(1, 30)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')

    def validate_username(self, field):
        if not User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is not existed.')


class RegisterForm(FlaskForm):
    username = StringField(
        'Username', validators=[
            DataRequired(), Length(1, 20),
            Regexp('^[a-zA-Z0-9]*$', message='The username should contain only a-z, A-Z and 0-9.')]
    )
    realname = StringField('Realname',
                           validators=[DataRequired(), Length(1, 20)])
    permission = RadioField(
        'Permission', validators=[DataRequired()],
        choices=[('Teacher', 'As teacher user'),
                 ('Admin', 'As administrator user'),
                 ('Root', 'As root user')],
        default='Teacher'
    )
    remark = CKEditorField('Remark')
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField()

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')

    def validate_permission(self, field):
        if not field.data or field.data not in ['Teacher', 'Admin', 'Root']:
            raise ValidationError(
                'The permission must select from Teacher, Admin and Root.')


class ChangeUsernameForm(FlaskForm):
    username = StringField(
        'New Username',
        validators=[
            DataRequired(), Length(1, 30), EqualTo('username2'),
            Regexp('^[a-zA-Z0-9]*$', message='The username should contain only a-z, A-Z and 0-9.')]
    )
    username2 = StringField(
        'Confirm Username',
        validators=[DataRequired()]
    )
    submit = SubmitField()

    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')


class EditProfileForm(FlaskForm):
    realname = StringField(
        'Realname',
        validators=[DataRequired(), Length(1, 30)]
    )
    remark = CKEditorField('Remark')
    submit = SubmitField()


class RootEditProfileForm(FlaskForm):
    username = StringField(
        'New Username',
        validators=[
            DataRequired(), Length(1, 30), EqualTo('username2'),
            Regexp('^[a-zA-Z0-9]*$', message='The username should contain only a-z, A-Z and 0-9.')]
    )
    username2 = StringField(
        'Confirm Username',
        validators=[DataRequired()]
    )

    realname = StringField(
        'Realname',
        validators=[DataRequired(), Length(1, 30)]
    )

    remark = CKEditorField('Remark')
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


class RootChangePasswordForm(FlaskForm):
    password = PasswordField(
        'New Password', validators=[DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField()


class AddUploadFileTypeForm(FlaskForm):
    file_type = StringField(
        'File type',
        validators=[
            DataRequired(), Length(1, 10),
            Regexp('^[a-z]*$', message='The file type should contain only a-z.')
        ])
    submit = SubmitField()

    def validate_file_type(self, field):
        if UploadFileType.query.filter_by(file_type=field.data).first():
            raise ValidationError('The file type is already in use.')
