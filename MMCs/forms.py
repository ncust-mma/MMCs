# -*- coding: utf-8 -*-

from flask_ckeditor import CKEditorField
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (BooleanField, FloatField, PasswordField, RadioField, IntegerField,
                     StringField, SubmitField, ValidationError, SelectMultipleField)
from wtforms.validators import (AnyOf, DataRequired, EqualTo, InputRequired,
                                Length, Regexp, NumberRange, Optional)

from MMCs.models import UploadFileType, User, Task


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(1, 30), InputRequired()])
    password = PasswordField(
        'Password', validators=[DataRequired(), InputRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')

    def validate_username(self, field):
        if not User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is not existed.')


class RegisterForm(FlaskForm):
    username = StringField(
        'Username', validators=[
            DataRequired(), Length(1, 20), InputRequired(),
            Regexp('^[a-zA-Z0-9]*$', message='The username should contain only a-z, A-Z and 0-9.')]
    )
    realname = StringField(
        'Realname',
        validators=[DataRequired(), Length(1, 20), InputRequired()])
    permission = RadioField(
        'Permission', validators=[
            DataRequired(), InputRequired(), AnyOf(['Teacher', 'Admin', 'Root'])],
        choices=[('Teacher', 'As teacher user'),
                 ('Admin', 'As administrator user'),
                 ('Root', 'As root user')],
        default='Teacher'
    )
    remark = CKEditorField('Remark', validators=[Optional()])
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(8, 128), EqualTo('password2'), InputRequired()])
    password2 = PasswordField(
        'Confirm password',
        validators=[DataRequired(), InputRequired()])
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
            InputRequired(), DataRequired(), Length(1, 30), EqualTo('username2'),
            Regexp('^[a-zA-Z0-9]*$', message='The username should contain only a-z, A-Z and 0-9.')]
    )
    username2 = StringField(
        'Confirm Username',
        validators=[DataRequired(), InputRequired()]
    )
    submit = SubmitField()

    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')


class EditProfileForm(FlaskForm):
    realname = StringField(
        'Realname',
        validators=[InputRequired(), DataRequired(), Length(1, 30)]
    )
    remark = CKEditorField('Remark', validators=[Optional()])
    submit = SubmitField()


class RootEditProfileForm(FlaskForm):
    username = StringField(
        'New Username',
        validators=[
            InputRequired(), DataRequired(), Length(1, 30), EqualTo('username2'),
            Regexp('^[a-zA-Z0-9]*$', message='The username should contain only a-z, A-Z and 0-9.')]
    )
    username2 = StringField(
        'Confirm Username',
        validators=[DataRequired(), InputRequired()]
    )

    realname = StringField(
        'Realname',
        validators=[InputRequired(), DataRequired(), Length(1, 30)]
    )

    remark = CKEditorField('Remark')
    submit = SubmitField()

    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        'Old Password', validators=[DataRequired(), InputRequired()])
    password = PasswordField(
        'New Password',
        validators=[InputRequired(), DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), InputRequired()])
    submit = SubmitField()


class RootChangePasswordForm(FlaskForm):
    password = PasswordField(
        'New Password',
        validators=[InputRequired(), DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField(
        'Confirm Password',
        validators=[InputRequired(), DataRequired()])
    submit = SubmitField()


class AddUploadFileTypeForm(FlaskForm):
    file_type = StringField(
        'File type',
        validators=[
            InputRequired(), DataRequired(), Length(1, 10),
            Regexp('^[a-z]*$', message='The file type should contain only a-z.')
        ])
    submit = SubmitField()

    def validate_file_type(self, field):
        if UploadFileType.query.filter_by(file_type=field.data).first():
            raise ValidationError('The file type is already in use.')


class ChangeScoreForm(FlaskForm):
    id = IntegerField(
        'Task ID',
        validators=[DataRequired()]
    )
    score = FloatField(
        'Score',
        validators=[InputRequired(), DataRequired(), NumberRange(0, 100)])
    submit = SubmitField()

    def validate_id(self, field):
        if Task.query.get(field.data) is None:
            raise ValidationError('The task is not existed.')


class AdminAddTaskForm(FlaskForm):
    id = IntegerField(
        'Task ID',
        validators=[DataRequired()])
    submit = SubmitField('Add')
