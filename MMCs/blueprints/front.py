# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user, login_fresh, confirm_login

from MMCs.extensions import db
from MMCs.models import User
from MMCs.utils import redirect_back

front_bp = Blueprint('front', __name__)


@front_bp.route('/')
def index():
    return render_template('front/index.html')


@front_bp.route('/about')
def about():
    return render_template('front/about.html')


@front_bp.route('/faq')
def faq():
    return render_template('front/faq.html')
