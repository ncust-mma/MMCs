# -*- coding: utf-8 -*-

from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import (FloatField, IntegerField, SubmitField, TextField,
                     ValidationError)
from wtforms.validators import DataRequired, InputRequired, Optional

from MMCs.models import Task


class ChangeScoreForm(FlaskForm):
    id = IntegerField(
        _l('Task ID'),
        validators=[DataRequired()]
    )

    score = FloatField(
        _l('Score'),
        validators=[DataRequired(), InputRequired()]
    )

    remark = TextField(
        _l('Remark'),
        validators=[Optional()],
        render_kw={'placeholder': _l('Leave your ideas')}
    )

    submit = SubmitField(_l('Change'))

    def validate_id(self, field):
        if Task.query.get(field.data) is None:
            raise ValidationError(_l('The task is not existed.'))
