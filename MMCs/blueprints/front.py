# -*- coding: utf-8 -*-

from flask import (Blueprint, abort, current_app, flash, jsonify,
                   make_response, redirect, render_template, url_for)
from flask_babel import _
from flask_login import current_user

from MMCs.extensions import db
from MMCs.utils import redirect_back

front_bp = Blueprint('front', __name__)


@front_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_root:
            return redirect(url_for('root.index'))
        elif current_user.is_admin:
            return redirect(url_for('admin.index'))
        elif current_user.is_teacher:
            return redirect(url_for('teacher.index'))
    return render_template('front/index.html')


@front_bp.route('/about')
def about():
    return render_template('front/about.html')


@front_bp.route('/set-locale/<locale>')
def set_locale(locale):
    if locale not in current_app.config['MMCS_LOCALES']:
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('locale', locale, max_age=60 * 60 * 24 * 30)

    if current_user.is_authenticated:
        current_user.locale = locale
        db.session.commit()

    flash(_('Setting updated.'), 'success')

    return response


@front_bp.route('/404')
def test():
    pass
