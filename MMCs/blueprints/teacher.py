# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from MMCs.decorators import teacher_required
from MMCs.models import Distribution, User

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/')
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


@teacher_bp.route('/score-management')
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

    return render_template('backstage/teacher/score_management.html', pagination=pagination, distributions=distributions, page=page, per_page=per_page)
