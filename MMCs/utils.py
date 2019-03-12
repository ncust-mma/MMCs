# -*- coding: utf-8 -*-

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import os
import random
import uuid

from flask import current_app, flash, redirect, request, url_for
from flask_babel import _
from pypinyin import lazy_pinyin
from werkzeug.utils import secure_filename

from MMCs.extensions import scheduler


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


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            name = getattr(form, field).label.text
            flash(_(
                "Error in the %(name)s field - %(error)s.", name=name, error=error), 'dark')


def gen_uuid(filename):
    ext = os.path.splitext(filename)[1]
    name = uuid.uuid1().hex + ext

    return name


def new_filename(filename):
    filename = secure_filename(''.join(lazy_pinyin(filename)))
    uuid = gen_uuid(filename)

    return filename, uuid


def check_filename(filename):
    flag = False
    info = _('Invalid filename.')
    if 5 >= filename.count('_') >= 2:
        problem = filename.split('_')[1]
        if problem.isalpha() and len(problem) == 1 and problem.isupper():
            number = filename.split('_')[2]
            if number.isdigit():
                flag = True
            else:
                info = _('Team number is not right.')
        else:
            info = _('Problem is not right.')

    return flag, info


def random_sample(teacher_task_number, this_problem, teachers_view):
    is_empty = sum(teacher_problem[this_problem]
                   for teacher_problem in teachers_view.values())
    solution_task_number = current_app.config['SOLUTION_TASK_NUMBER']
    if is_empty == 0:
        teacher_ids = random.sample(
            list(teachers_view), solution_task_number)
    else:
        teacher_ids = []
        for teacher_id, teacher_problem in teachers_view.items():
            if teacher_problem[this_problem] and teacher_problem[this_problem] < teacher_task_number:
                teacher_ids.append(teacher_id)

            if len(teacher_ids) >= solution_task_number:
                break

    for teacher_id in teacher_ids:
        teachers_view[teacher_id][this_problem] += 1

    for teacher_id in list(teachers_view.keys()):
        teacher_problem = teachers_view[teacher_id]
        if sum(teacher_problem.values()) >= teacher_task_number:
            teachers_view.pop(teacher_id)

    return teacher_ids


@scheduler.task('interval', id='clear_cache', weeks=4)
def clear_cache():
    with scheduler.app.app_context():
        for root, _, files in os.walk(current_app.config['FILE_CACHE_PATH']):
            for file in files:
                if file != '.gitkeep':
                    path = os.path.join(root, file)
                    os.remove(path)
