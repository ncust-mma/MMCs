# -*- coding: utf-8 -*-

from flask import Blueprint, flash, render_template, request
from flask_login import (confirm_login, current_user, login_fresh,
                         login_required, login_user, logout_user)

from MMCs.decorators import root_required
from MMCs.extensions import db
from MMCs.forms import LoginForm
from MMCs.models import User, Solution, User
from MMCs.settings import Operations
from MMCs.utils import generate_token, redirect_back, validate_token


root_bp = Blueprint('root', __name__)


@root_bp.route('/root')
@login_required
@root_required
def index():
    return render_template('backstage/root/overview.html')


@root_bp.route('/root/task-management')
@login_required
@root_required
def task_management():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Solution.query.order_by(
        Solution.id.desc()).paginate(page, per_page)
    solutions = pagination.items

    if request.method == 'POST' and 'file' in request.files:
        f = request.files.get('file')
        pass

    return render_template('backstage/root/task_management.html', pagination=pagination, solutions=solutions)


@root_bp.route('/root/score-management')
@login_required
@root_required
def score_management():

    return render_template('backstage/root/score_management.html')


@root_bp.route('/root/personnel-management')
@login_required
@root_required
def personnel_management():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = User.query.order_by(User.id.desc()).paginate(page, per_page)
    pagination = User.query.filter(User.id!=current_user.id).order_by(User.id.desc()).paginate(page, per_page)
    users = pagination.items

    return render_template('backstage/root/personnel_management.html', pagination=pagination, users=users)


@root_bp.route('/root/competition-management')
@login_required
@root_required
def competition_management():
    return render_template('backstage/root/competition_management.html')


@root_bp.route('/root/system-settings')
@login_required
@root_required
def system_settings():
    return render_template('backstage/root/system_settings.html')
