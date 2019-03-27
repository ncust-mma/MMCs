# -*- coding: utf-8 -*-

from flask_babel import lazy_gettext as _l
from flask_ckeditor import CKEditorField
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import (DataRequired, EqualTo, InputRequired, Length,
                                Optional, Regexp)

from MMCs.models import User


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
