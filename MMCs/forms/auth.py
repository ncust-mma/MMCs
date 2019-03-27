# -*- coding: utf-8 -*-

from flask_babel import lazy_gettext as _l
from flask_ckeditor import CKEditorField
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (BooleanField, FloatField, IntegerField, PasswordField,
                     RadioField, StringField, SubmitField, TextField,
                     ValidationError)
from wtforms.validators import (AnyOf, DataRequired, EqualTo, InputRequired,
                                Length, Optional, Regexp)

from MMCs.models import Task, User


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
