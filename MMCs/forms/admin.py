# -*- coding: utf-8 -*-

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SubmitField


class ButtonAddForm(FlaskForm):
    submit = SubmitField(_l('Add'))
