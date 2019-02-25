# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, Blueprint
from flask_login import current_user, login_fresh

from MMCs.models import User


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


@front_bp.route('/faq')
def faq():
    return render_template('front/faq.html')
