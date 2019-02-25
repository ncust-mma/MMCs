# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request
from flask_login import login_required

from MMCs.decorators import admin_required
from MMCs.extensions import db
from MMCs.models import Solution, Distribution


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
@admin_required
def index():
    distribution = Distribution.query.filter(Distribution.year == 2019).all()
    teacher_ids = list(set([i.teacher_id for i in distribution]))
    count = 0

    for teacher_id in teacher_ids:
        solutions_right = Distribution.query.filter(
            Distribution.year == 2019,
            Distribution.teacher_id == teacher_id,
            Distribution.point != None).count()

        solutions_all = Distribution.query.filter(
            Distribution.year == 2019,
            Distribution.teacher_id == teacher_id).count()
        if solutions_right == solutions_all:
            count += 1

    progress = "{:.2f}%".format(count/len(teacher_ids)*100)

    return render_template('backstage/admin/overview.html')


@admin_bp.route('/task-management', methods=['GET', 'POST'])
@login_required
@admin_required
def task_management():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Solution.query.order_by(
        Solution.id.desc()).paginate(page, per_page)
    solutions = pagination.items

    if request.method == 'POST' and 'file' in request.files:
        f = request.files.get('file')

    return render_template('backstage/admin/task_management.html', pagination=pagination, solutions=solutions)


@admin_bp.route('/score-management')
@login_required
@admin_required
def score_management():

    return render_template('backstage/admin/score_management.html')
