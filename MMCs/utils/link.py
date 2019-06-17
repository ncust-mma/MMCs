# -*- coding: utf-8 -*-

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import os
from random import sample

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
