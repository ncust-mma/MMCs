# -*- coding: utf-8 -*-

from flask import request
from flask_login import current_user

from MMCs.extensions import db
from MMCs.models import Log


def log_user(content):
    log = Log(
        user_id=current_user.id,
        ip=request.remote_addr,
        content=content
    )

    db.session.add(log)
    db.session.commit()
