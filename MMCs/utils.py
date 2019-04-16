# -*- coding: utf-8 -*-

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import os
from random import sample

import numba as nb
from flask import (Markup, abort, current_app, flash, redirect,
                   render_template_string, request, url_for)
from flask_babel import _
from flask_login import current_user

from MMCs.extensions import db
from MMCs.models import Competition, Log, User


def is_safe_url(target):
    """Check this url is safe or not?

    Arguments:
        target {str} -- url

    Returns:
        bool -- `True` means it is safe
    """

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='front.index', **kwargs):
    """Redirect to last url

    Keyword Arguments:
        default {str} -- default url (default: {'front.index'})

    Returns:
        Response
    """

    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def allowed_file(filename):
    """Check file type is allowed or not?
    """

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_SOLUTION_EXTENSIONS']


def flash_errors(form):
    """flash errors in form
    """

    for field, errors in form.errors.items():
        for error in errors:
            name = getattr(form, field).label.text
            flash(
                _("Error in the %(name)s field - %(error)s.", name=name, error=error), 'dark')


def gen_uuid(filename):
    """Generate uuid from upload filename

    Arguments:
        filename {str} -- upload filename

    Returns:
        str -- uuid
    """
    from uuid import uuid1

    ext = os.path.splitext(filename)[1]
    name = uuid1().hex + ext

    return name


def new_filename(filename):
    """Return secure filename from upload filename

    Arguments:
        filename {str} -- upload filename
    """
    from pypinyin import lazy_pinyin
    from werkzeug.utils import secure_filename

    filename = secure_filename(''.join(lazy_pinyin(filename)))

    return filename, gen_uuid(filename)


def check_filename(filename):
    """Check filename is secure or not

    Arguments:
        filename {str} -- upload filename
    """

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


def cal_teacher_task_number():
    """Calculate the max teacher gottn task numbers

    Returns:
        int -- task number
    """
    from math import ceil

    com = Competition.current_competition()
    task_number = ceil(
        len(com.solutions) * current_app.config['SOLUTION_TASK_NUMBER'] / len(User.teachers()))

    return task_number


@nb.jit
def gen_teacher_view(this_problem):
    """Generate such as {teacher id: {problem : number}} dictionary

    Arguments:
        this_problem {str} -- current solution problem
    """

    teachers_view = {}
    is_notempty = 0
    for teacher in User.teachers():
        teacher_tasks = teacher.current_all_tasks
        if len(teacher_tasks) < cal_teacher_task_number():
            teacher_task_problems = teacher.current_task_problems
            teachers_view[teacher.id] = teacher_task_problems
            is_notempty += teacher_task_problems[this_problem]

    return teachers_view, is_notempty


@nb.jit
def _random_sample(this_problem, teachers_view, is_notempty):
    """Get random sample teacher to task

    Arguments:
        this_problem {str} -- current solution problem
        teachers_view {dic} -- a data structure
        is_notempty {bool} -- teachers_view no empty flag

    Returns:
        list -- sample teachers' id
    """

    solution_task_number = current_app.config['SOLUTION_TASK_NUMBER']
    if is_notempty:
        teacher_ids = []
        for teacher_id, teacher_problem in teachers_view.items():
            if (len(teacher_ids) <= solution_task_number and
                    teacher_problem[this_problem] and
                    teacher_problem[this_problem] < cal_teacher_task_number()):
                teacher_ids.append(teacher_id)
    else:

        teacher_ids = sample(teachers_view.keys(), solution_task_number)

    return teacher_ids


def random_sample(this_problem):
    """front function, api for `_random_sample`
    """

    teachers_view, is_notempty = gen_teacher_view(this_problem)

    return _random_sample(this_problem, teachers_view, is_notempty)


def zip2here(input_path, output_path):
    """pack a file or folder to dis path

    Arguments:
        input_path {str}
        output_path {str}
    """

    from zipfile import ZipFile

    with ZipFile(output_path, 'w') as z:
        if os.path.isdir(input_path):
            for root, _, files in os.walk(input_path):
                for file in files:
                    if file == '.gitkeep':
                        continue
                    z.write(os.path.join(root, file), file)

        elif os.path.isfile(input_path):
            z.write(input_path, os.path.split(input_path)[1])
        else:
            abort(404)


def write_localfile(path, content, is_markup=True):
    with open(path, 'w', encoding='utf-8') as f:
        if is_markup:
            content = Markup(content)
        f.write(content)


def read_localfile(path, is_render=True):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        if is_render:
            content = render_template_string(content)

    return content


def log_user(content):
    log = Log(
        user_id=current_user.id,
        ip=request.remote_addr,
        content=content
    )

    db.session.add(log)
    db.session.commit()
