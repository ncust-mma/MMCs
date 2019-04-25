# -*- coding: utf-8 -*-

from flask import flash
from flask_babel import _


def flash_errors(form):
    """flash errors in form
    """

    for field, errors in form.errors.items():
        for error in errors:
            name = getattr(form, field).label.text
            flash(
                _("Error in the %(name)s field - %(error)s.", name=name, error=error), 'dark')
