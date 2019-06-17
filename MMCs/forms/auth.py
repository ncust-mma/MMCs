# -*- coding: utf-8 -*-

from flask import flash
from flask_babel import _
from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import (BooleanField, PasswordField, StringField, SubmitField,
                     ValidationError)
from wtforms.validators import DataRequired, InputRequired, Length

from MMCs.extensions import captcha
from MMCs.models import User


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
    captcha = StringField(_l('Captcha'))
    remember_me = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Log in'))

    def validate_username(self, field):
        if not User.query.filter_by(username=field.data).first():
            raise ValidationError(_l('Invalid username or password.'))

    def validate_captcha(self, field):
        if not captcha.validate():
            flash(_('Invalid captcha.'), 'warning')
            raise ValidationError(_l('Invalid captcha.'))
