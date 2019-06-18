# -*- coding: utf-8 -*-

from flask import Blueprint, current_app, flash, render_template, request
from flask_babel import _
from flask_login import current_user, login_required

from MMCs.decorators import teacher_required
from MMCs.extensions import db
from MMCs.forms.teacher import ChangeScoreForm
from MMCs.models import Competition, Solution, Task
from MMCs.utils.link import redirect_back
from MMCs.utils.table import flash_errors

teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.before_request
@teacher_required
@login_required
def login_protect():
    pass


@teacher_bp.route('/')
def index():
    com = Competition.current_competition()
    if com and com.is_start():
        task_all = Task.query.filter(
            Task.competition_id == com.id,
            Task.teacher_id == current_user.id).count()

        task_finished = 0
        if task_all:
            task_finished = Task.query.filter(
                Task.competition_id == com.id,
                Task.teacher_id == current_user.id,
                Task.score).count()

        return render_template(
            'backstage/teacher/overview.html', task_finished=task_finished, task_all=task_all)

    return render_template('backstage/teacher/overview.html')


@teacher_bp.route('/task')
def manage_task():
    com = Competition.current_competition()
    if com:
        page = request.args.get('page', 1, type=int)
        form = ChangeScoreForm()

        pagination = Task.query.filter(
            Task.competition_id == com.id,
            Task.teacher_id == current_user.id
        ).join(Solution).order_by(Solution.name).paginate(page, current_app.config['SOLUTION_PER_PAGE'])

        return render_template(
            'backstage/teacher/manage_task.html',
            pagination=pagination, page=page, form=form)

    return render_template('backstage/teacher/manage_task.html')


@teacher_bp.route('/task/change/<int:task_id>', methods=['POST'])
def change(task_id):
    form = ChangeScoreForm()
    upper = current_app.config['SCORE_UPPER_LIMIT']
    lower = current_app.config['SCORE_LOWER_LIMIT']
    if form.validate_on_submit:
        if lower <= form.score.data <= upper:
            task = Task.query.get_or_404(task_id)
            task.score = form.score.data
            task.remark = form.remark.data
            db.session.commit()

            flash(_('Score Updated.'), 'success')
        else:
            flash(
                _('Score out of range from %(lower)s to %(upper)s.',
                  lower=lower, upper=upper),
                'warning')

    flash_errors(form)
    return redirect_back()
