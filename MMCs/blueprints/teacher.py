# -*- coding: utf-8 -*-

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from MMCs.decorators import teacher_required
from MMCs.extensions import db
from MMCs.forms import ChangeScoreForm
from MMCs.models import Distribution, User
from MMCs.utils import flash_errors, redirect_back

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/')
@login_required
@teacher_required
def index():
    solutions_right = Distribution.query.filter(
        Distribution.year == 2019,
        Distribution.teacher_id == current_user.id,
        Distribution.score != None,
        Distribution.score != '').count()

    solutions_all = Distribution.query.filter(
        Distribution.year == 2019,
        Distribution.teacher_id == current_user.id).count()

    progress = False
    if solutions_all:
        progress = solutions_right/solutions_all*100

    return render_template('backstage/teacher/overview.html', progress=progress)


@teacher_bp.route('/score-management', methods=['GET', 'POST'])
@login_required
@teacher_required
def score_management():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SOLUTION_PER_PAGE']
    pagination = Distribution.query.filter(
        Distribution.year == 2019,
        Distribution.teacher_id == current_user.id
    ).order_by(Distribution.id.desc()).paginate(page, per_page)
    distributions = pagination.items

    form = ChangeScoreForm()
    if form.validate_on_submit():
        distribution = Distribution.query.get(form.id.data)
        distribution.score = form.score.data
        db.session.commit()

        flash('Score Updated.', 'info')
        return redirect_back()

    flash_errors(form)
    return render_template(
        'backstage/teacher/score_management.html',
        pagination=pagination, distributions=distributions,
        page=page, per_page=per_page, form=form)
