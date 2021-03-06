# -*- coding: utf-8 -*-

from flask_babel import lazy_gettext as _l
from flask_ckeditor import CKEditorField
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (IntegerField, PasswordField, RadioField, StringField,
                     SubmitField, ValidationError)
from wtforms.validators import (AnyOf, DataRequired, EqualTo, InputRequired,
                                Length, Optional, Regexp)

from MMCs.models import User


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
        _l('Permission'),
        validators=[DataRequired(),
                    InputRequired(),
                    AnyOf(['Teacher', 'Admin', 'Root'])],
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


class AccountImportForm(FlaskForm):
    file = FileField(
        _l("Account"),
        validators=[
            FileRequired(),
            FileAllowed(['xls', 'xlsx'], _l('xls or xlsx only!'))
        ]
    )

    upload = SubmitField(_l('Upload'))


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


class NoticeEditForm(FlaskForm):
    notice = CKEditorField(_l('Notice'), validators=[Optional()])
    edit = SubmitField(_l('Edit'))


class AboutEditForm(FlaskForm):
    about = CKEditorField(_l('About'), validators=[Optional()])
    edit = SubmitField(_l('Edit'))


class CompetitionSettingForm(FlaskForm):
    solution_task_number = IntegerField(
        _l('SOLUTION TASK NUMBER'), validators=[Optional()])
    user_per_page = IntegerField(
        _l('USER PER PAGE'), validators=[Optional()])
    solution_per_page = IntegerField(
        _l('SOLUTION PER PAGE'), validators=[Optional()])
    competition_per_page = IntegerField(
        _l('COMPETITION PER PAGE'), validators=[Optional()])
    dropzone_max_files = IntegerField(
        _l('DROPZONE MAX FILES'), validators=[Optional()])

    submit = SubmitField(_l('Submit'))


class AboutImageUploadForm(FlaskForm):
    file = FileField(
        _l("About Image"),
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'jpeg', 'png'], _l('jpg, jpeg or png only!'))
        ]
    )

    about_upload = SubmitField(_l('Upload'))


class ErrorImageUploadForm(FlaskForm):
    file = FileField(
        _l("Error Image"),
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'jpeg', 'png'], _l('jpg, jpeg or png only!'))
        ]
    )

    error_upload = SubmitField(_l('Upload'))


class IndexImageUploadForm(FlaskForm):
    file = FileField(
        _l("Index Image"),
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'jpeg', 'png'], _l('jpg, jpeg or png only!'))
        ]
    )

    index_upload = SubmitField(_l('Upload'))


class CompetitionNameForm(FlaskForm):
    name = StringField(
        _l('Competition name'),
        validators=[InputRequired(), DataRequired(), Length(1, 30)]
    )
    submit = SubmitField(_l('Submit'))


class DownloadLogForm(FlaskForm):
    download = SubmitField(_l('Download logs'))
