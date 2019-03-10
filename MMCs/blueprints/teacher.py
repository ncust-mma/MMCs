# -*- coding: utf-8 -*-

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_babel import _
from flask_login import current_user, login_required

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
    if com:
        finished = Task.query.filter(
            Task.competition_id == com.id,
            Task.teacher_id == current_user.id,
            Task.score != None,
            Task.score != '').count()

        task_number = Task.query.filter(
            Task.competition_id == com.id,
            Task.teacher_id == current_user.id).count()

        progress = finished/task_number*100
    else:
        progress = task_number = 0
    return render_template('backstage/teacher/overview.html', progress=progress, task_number=task_number)


@teacher_bp.route('/manage-task', methods=['GET', 'POST'])
@login_required
@teacher_required
def manage_task():
    com = Competition.current_competition()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SOLUTION_PER_PAGE']
    form = ChangeScoreForm()
    if com:
        pagination = Task.query.filter(
            Task.competition_id == com.id,
            Task.teacher_id == current_user.id
        ).order_by(Task.id.desc()).paginate(page, per_page)
        tasks = pagination.items

        if form.validate_on_submit():
            upper = current_app.config['SCORE_UPPER_LIMIT']
            lower = current_app.config['SCORE_LOWER_LIMIT']
            if lower <= form.score.data <= upper:
                task = Task.query.get_or_404(form.id.data)
                task.score = form.score.data
                db.session.commit()

                flash(_('Score Updated.'), 'success')
            else:
                flash(_(
                    'Score out of range from %(lower)s to %(upper)s.', lower=lower, upper=upper), 'warning')

            return redirect_back()
        flash_errors(form)

    return render_template(
        'backstage/teacher/manage_task.html',
        pagination=pagination, tasks=tasks,
        page=page, per_page=per_page, form=form)
