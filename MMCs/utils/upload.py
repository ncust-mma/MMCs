# -*- coding: utf-8 -*-

import os

from flask import current_app
from flask_babel import _


def allowed_file(filename):
    """Check file type is allowed or not?
    """

    return ('.' in filename
            and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_SOLUTION_EXTENSIONS'])


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
