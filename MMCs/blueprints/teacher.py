# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request
from flask_login import (confirm_login, current_user, login_fresh,
                         login_required, login_user, logout_user)

from MMCs.decorators import teacher_required
from MMCs.extensions import db
from MMCs.forms import LoginForm
from MMCs.models import Distribution, User
from MMCs.settings import Operations
from MMCs.utils import generate_token, redirect_back, validate_token

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/teacher')
@login_required
@teacher_required
def index():
    solutions_right = Distribution.query.filter(
        Distribution.year == 2019,
        Distribution.teacher_id == current_user.id,
        Distribution.point != None).count()

    solutions_all = Distribution.query.filter(
        Distribution.year == 2019,
        Distribution.teacher_id == current_user.id).count()

    progress = False
    if solutions_all:
        progress = "{:.2f}%".format(solutions_right/solutions_all*100)

    return render_template('backstage/teacher/overview.html', progress=progress)


@teacher_bp.route('/teacher/score-management')
@login_required
@teacher_required
def score_management():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Distribution.query.filter(
        Distribution.year == 2019,
        Distribution.teacher_id == current_user.id
    ).order_by(Distribution.id.desc()).paginate(page, per_page)
    distributions = pagination.items

    return render_template('backstage/teacher/score_management.html', pagination=pagination, distributions=distributions)
