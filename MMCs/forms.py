# -*- coding: utf-8 -*-

from flask_babel import lazy_gettext as _l
from flask_ckeditor import CKEditorField
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (BooleanField, FloatField, IntegerField, PasswordField,
                     RadioField, StringField, SubmitField, ValidationError)
from wtforms.validators import (AnyOf, DataRequired, EqualTo, InputRequired,
                                Length, Optional, Regexp)

from MMCs.models import Task, UploadFileType, User


class LoginForm(FlaskForm):
    username = StringField(
        _l('Username'),
        validators=[
            DataRequired(),
            Length(1, 30),
            InputRequired()]
    )
    password = PasswordField(
        _l('Password'), validators=[DataRequired(), InputRequired()])
    remember_me = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Log in'))

    def validate_username(self, field):
        if not User.query.filter_by(username=field.data).first():
            raise ValidationError(_l('The username is not existed.'))


class RegisterForm(FlaskForm):
    username = StringField(
        _l('Username'), validators=[
            DataRequired(), Length(1, 20), InputRequired(),
            Regexp('^[a-zA-Z0-9]*$', message=_l('The username should contain only a-z, A-Z and 0-9.'))]
    )
    realname = StringField(
        _l('Realname'),
        validators=[DataRequired(), Length(1, 20), InputRequired()])
    permission = RadioField(
        _l('Permission'), validators=[
            DataRequired(), InputRequired(), AnyOf(['Teacher', 'Admin', 'Root'])],
        choices=[('Teacher', _l('As teacher user')),
                 ('Admin', _l('As administrator user')),
                 ('Root', _l('As root user'))],
        default='Teacher'
    )
    remark = CKEditorField(_l('Remark'), validators=[Optional()])
    password = PasswordField(
        _l('Password'),
        validators=[DataRequired(), Length(8, 128), EqualTo('password2'), InputRequired()])
    password2 = PasswordField(
        _l('Confirm password'),
        validators=[DataRequired(), InputRequired()])
    submit = SubmitField(_l('Register'))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(_l('The username is already in use.'))

    def validate_permission(self, field):
        if not field.data or field.data not in ['Teacher', 'Admin', 'Root']:
            raise ValidationError(_l(
                'The permission must select from Teacher, Admin and Root.'))


class ChangeUsernameForm(FlaskForm):
    username = StringField(
        _l('New Username'),
        validators=[
            InputRequired(), DataRequired(), Length(1, 30), EqualTo('username2'),
            Regexp('^[a-zA-Z0-9]*$', message=_l('The username should contain only a-z, A-Z and 0-9.'))]
    )
    username2 = StringField(
        _l('Confirm Username'),
        validators=[DataRequired(), InputRequired()]
    )
    submit = SubmitField(_l('Change'))

    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(_l('The username is already in use.'))


class EditProfileForm(FlaskForm):
    realname = StringField(
        _l('Realname'),
        validators=[InputRequired(), DataRequired(), Length(1, 30)]
    )
    remark = CKEditorField(_l('Remark'), validators=[Optional()])
    submit = SubmitField(_l('Edit'))


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(
        _l('Old Password'), validators=[DataRequired(), InputRequired()])
    password = PasswordField(
        _l('New Password'),
        validators=[InputRequired(), DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField(
        _l('Confirm Password'),
        validators=[DataRequired(), InputRequired()])
    submit = SubmitField(_l('Change'))


class RootChangePasswordForm(FlaskForm):
    password = PasswordField(
        _l('New Password'),
        validators=[InputRequired(), DataRequired(), Length(8, 128), EqualTo('password2')])
    password2 = PasswordField(
        _l('Confirm Password'),
        validators=[InputRequired(), DataRequired()])
    submit = SubmitField(_l('Change'))


class AddUploadFileTypeForm(FlaskForm):
    file_type = StringField(
        _l('File type'),
        validators=[
            InputRequired(), DataRequired(), Length(1, 10),
            Regexp('^[a-z]*$', message=_l('The file type should contain only a-z.'))
        ])
    submit = SubmitField(_l('Add'))

    def validate_file_type(self, field):
        if UploadFileType.query.filter_by(file_type=field.data).first():
            raise ValidationError(_l('The file type is already in use.'))


class ChangeScoreForm(FlaskForm):
    id = IntegerField(
        _l('Task ID'),
        validators=[DataRequired()]
    )

    score = FloatField(
        _l('Score'),
        validators=[
            InputRequired()]
    )
    submit = SubmitField(_l('Change'))

    def validate_id(self, field):
        if Task.query.get(field.data) is None:
            raise ValidationError(_l('The task is not existed.'))


class AdminAddTaskForm(FlaskForm):
    id = IntegerField(
        _l('Task ID'),
        validators=[DataRequired()])
    submit = SubmitField(_l('Add'))


class ButtonAddForm(FlaskForm):
    submit = SubmitField(_l('Add'))


class ButtonCheckForm(FlaskForm):
    submit = SubmitField(_l('Check'))


class ButtonStopForm(FlaskForm):
    submit = SubmitField(_l('Stop'))


class ButtonContinueForm(FlaskForm):
    submit = SubmitField(_l('Continue'))


class ButtonEditProfileForm(FlaskForm):
    submit = SubmitField(_l('Edit Profile'))


class ButtonChangeUsernameForm(FlaskForm):
    submit = SubmitField(_l('Change Username'))


class ButtonChangePasswordForm(FlaskForm):
    submit = SubmitField(_l('Change Password'))
