# -*- coding: utf-8 -*-

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_babel import _
from flask_login import current_user, login_required
from sqlalchemy import desc

from MMCs.decorators import teacher_required
from MMCs.extensions import db
from MMCs.forms import ChangeScoreForm
from MMCs.models import Competition, Task, User
from MMCs.utils import flash_errors, redirect_back

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/')
@login_required
@teacher_required
def index():
    com = Competition.current_competition()
    if com and com.is_start():
        progress = task_number = 0

        finished = Task.query.filter(
            Task.competition_id == com.id,
            Task.teacher_id == current_user.id,
            Task.score != None,
            Task.score != '').count()

        task_number = Task.query.filter(
            Task.competition_id == com.id,
            Task.teacher_id == current_user.id).count()

        if task_number:
            progress = finished/task_number*100

        return render_template('backstage/teacher/overview.html', progress=progress, task_number=task_number)

    return render_template('backstage/teacher/overview.html')


@teacher_bp.route('/task')
@login_required
@teacher_required
def manage_task():
    com = Competition.current_competition()
    if com:
        page = request.args.get('page', 1, type=int)
        form = ChangeScoreForm()

        pagination = Task.query.filter(
            Task.competition_id == com.id,
            Task.teacher_id == current_user.id
        ).order_by(Task.id.desc()).paginate(page, current_app.config['SOLUTION_PER_PAGE'])

        return render_template(
            'backstage/teacher/manage_task.html',
            pagination=pagination, page=page, form=form)

    return render_template('backstage/teacher/manage_task.html')


@teacher_bp.route('/task/change/<int:task_id>', methods=['POST'])
@login_required
@teacher_required
def change(task_id):
    form = ChangeScoreForm()
    upper = current_app.config['SCORE_UPPER_LIMIT']
    lower = current_app.config['SCORE_LOWER_LIMIT']
    if form.validate_on_submit:
        if form.score.data:
            if lower <= form.score.data <= upper:
                task = Task.query.get_or_404(task_id)
                task.score = form.score.data
                task.remark = form.remark.data
                db.session.commit()

                flash(_('Score Updated.'), 'success')
            else:
                flash(_(
                    'Score out of range from %(lower)s to %(upper)s.', lower=lower, upper=upper), 'warning')
        else:
            flash(_('Invalid score.'), 'warning')

    flash_errors(form)
    return redirect_back()
