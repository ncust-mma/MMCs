# -*- coding: utf-8 -*-

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import datetime
import os
import uuid

from flask import current_app, flash, redirect, request, url_for
from flask_babel import _
from pypinyin import lazy_pinyin
from werkzeug.utils import secure_filename

from MMCs.extensions import db


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='front.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_SOLUTION_EXTENSIONS']


def current_year():
    return datetime.datetime.now().year


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            name = getattr(form, field).label.text
            flash(_(
                "Error in the %(name)s field - %(error)s", name=name, error=error), 'dark')


def gen_uuid(filename):
    ext = os.path.splitext(filename)[1]
    name = uuid.uuid1().hex + ext

    return name


def new_filename(filename):
    filename = secure_filename(''.join(lazy_pinyin(filename)))
    uuid = gen_uuid(filename)

    return filename, uuid
