# -*- coding: utf-8 -*-

import os

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, send_file, url_for)
from flask_babel import _
from flask_login import fresh_login_required, login_required

from MMCs.decorators import admin_required
from MMCs.extensions import db
from MMCs.forms.admin import ButtonAddForm
from MMCs.models import Competition, Solution, Task, User
from MMCs.utils import (allowed_file, check_filename, download_solution_score,
                        download_teacher_result, log_user, new_filename,
                        random_sample, redirect_back)

admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
@admin_required
@login_required
def login_protect():
    pass


@admin_bp.route('/')
def index():
    com = Competition.current_competition()
    if com and com.is_start():
        tasks = com.tasks
        task_all = task_finished = 0
        if tasks:
            task_all = len(tasks)
            task_finished = len([
                task for task in tasks if task.score is not None])

        return render_template(
            'backstage/admin/overview.html', task_finished=task_finished, task_all=task_all)

    return render_template('backstage/admin/overview.html')


@admin_bp.route('/solution')
def manage_solution():
    return redirect(url_for('admin.solution_list'))


@admin_bp.route('/solution/list')
def solution_list():
    com = Competition.current_competition()
    if com:
        page = request.args.get('page', 1, type=int)
        pagination = Solution.query.filter_by(competition_id=com.id).order_by(
            Solution.id.desc()).paginate(page, current_app.config['SOLUTION_PER_PAGE'])

        form = ButtonAddForm()

        return render_template(
            'backstage/admin/manage_solution/solution_list.html',
            pagination=pagination, page=page, form=form)

    return render_template('backstage/admin/manage_solution/solution_list.html')


@admin_bp.route('/solution/upload', methods=['GET', 'POST'])
@fresh_login_required
def upload():
    if request.method == 'POST' and 'file' in request.files:
        content = render_template('logs/admin/solution/upload.txt')
        log_user(content)

        if Competition.is_start():
            file = request.files.get('file')
            filename, uuid = new_filename(file.filename)
            if allowed_file(filename):
                flag, info = check_filename(filename)
                if flag:
                    path = current_app.config['SOLUTION_SAVE_PATH']
                    file.save(os.path.join(path, uuid))

                    com = Competition.current_competition()
                    solution = Solution(
                        name=filename, uuid=uuid, competition_id=com.id)
                    db.session.add(solution)
                    db.session.commit()
                else:
                    return info, 400
            else:
                ext = current_app.config['ALLOWED_SOLUTION_EXTENSIONS']
                return '{} only!'.format(', '.join(ext)), 400
        else:
            return _("Competition of current year don't start."), 403

    return render_template('backstage/admin/manage_solution/upload.html')


@admin_bp.route('/solution/delete/<int:solution_id>', methods=['POST'])
@fresh_login_required
def delete_solution_task(solution_id):
    solution = Solution.query.get_or_404(solution_id)
    db.session.delete(solution)
    db.session.commit()

    content = render_template('logs/admin/solution/delete.txt')
    log_user(content)

    flash(_('Solution deleted.'), 'info')
    return redirect_back()


@admin_bp.route('/task')
def manage_task():
    return redirect(url_for('admin.teacher_view'))


@admin_bp.route('/task/method', methods=['GET', 'POST'])
def method():
    return render_template('backstage/admin/manage_task/method.html')


@admin_bp.route('/task/method/random', methods=['POST'])
@fresh_login_required
def method_random():
    content = render_template('logs/admin/solution/random.txt')
    log_user(content)

    com = Competition.current_competition()
    Task.query.filter_by(competition_id=com.id).delete()
    db.session.commit()

    solutions = com.solutions
    if solutions:
        teachers = User.teachers()
        if teachers:
            solutions = sorted(solutions, key=lambda x: x.problem)
            for solution in solutions:
                this_problem = solution.problem
                for teacher_id in random_sample(this_problem):
                    task = Task(
                        teacher_id=teacher_id,
                        solution_id=solution.id,
                        competition_id=com.id
                    )
                    db.session.add(task)
                    try:
                        db.session.commit()
                    except:
                        db.session.rollback()

            flash(_('Randomly assigned.'), 'success')
        else:
            flash(_('Please add teacher to assign task.'), 'warning')
    else:
        flash(_('No solutions.'), 'warning')

    return redirect_back()


@admin_bp.route('/task/teacher')
def teacher_view():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.filter(User.permission == 'Teacher').order_by(
        User.id.desc()).paginate(page, current_app.config['USER_PER_PAGE'])

    add_form = ButtonAddForm()

    return render_template(
        'backstage/admin/manage_task/teacher_view.html',
        pagination=pagination, page=page, add_form=add_form)


@admin_bp.route('/task/teacher/check/<int:user_id>/tasks')
def check_user(user_id):
    content = render_template('logs/admin/task/check.txt')
    log_user(content)

    com = Competition.current_competition()
    page = request.args.get('page', 1, type=int)

    pagination = Task.query.filter(
        Task.teacher_id == user_id,
        Task.competition_id == com.id
    ).order_by(Task.id.desc()).paginate(page, current_app.config['SOLUTION_PER_PAGE'])

    return render_template(
        'backstage/admin/manage_task/check.html',
        pagination=pagination, page=page)


@admin_bp.route('/task/teacher/delete/<int:user_id>', methods=['POST'])
@fresh_login_required
def delete_user_task(user_id):
    content = render_template('logs/admin/task/clean.txt')
    log_user(content)

    com = Competition.current_competition()
    Task.query.filter(
        Task.teacher_id == user_id,
        Task.competition_id == com.id).delete()
    db.session.commit()

    flash(_("All tasks of User deleted."), 'success')
    return redirect_back()


@admin_bp.route('/task/teacher/check/delete/<int:task_id>', methods=['POST'])
@fresh_login_required
def method_delete_task(task_id):
    content = render_template('logs/admin/task/delete.txt')
    log_user(content)

    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()

    flash(_('Task deleted.'), 'success')
    return redirect_back()


@admin_bp.route('/task/teacher/check/<int:user_id>/add', methods=['GET', 'POST'])
def task_add_list(user_id):
    page = request.args.get('page', 1, type=int)
    com = Competition.current_competition()
    user = User.query.get_or_404(user_id)
    solution_ids = set(
        task.solution_id for task in user.current_all_tasks)

    pagination = Solution.query.filter(
        ~Solution.id.in_(map(str, solution_ids)),
        Solution.competition_id == com.id
    ).order_by(Solution.name).paginate(page, current_app.config['SOLUTION_PER_PAGE'])

    return render_template(
        'backstage/admin/manage_task/add.html',
        pagination=pagination, page=page, user_id=user.id)


@admin_bp.route('/task/teacher/check/<int:user_id>/add/<int:solution_id>', methods=['POST'])
@fresh_login_required
def task_add(user_id, solution_id):
    content = render_template('logs/admin/task/add.txt')
    log_user(content)

    com = Competition.current_competition()
    task = Task(
        teacher_id=user_id,
        solution_id=solution_id,
        competition_id=com.id
    )
    db.session.add(task)
    db.session.commit()

    flash(_('Added successed.'), 'success')
    return redirect_back()


@admin_bp.route('/task/solution')
def solution_view():
    page = request.args.get('page', 1, type=int)
    com = Competition.current_competition()
    pagination = Solution.query.filter_by(competition_id=com.id).order_by(
        Solution.name).paginate(page, current_app.config['SOLUTION_PER_PAGE'])

    return render_template(
        'backstage/admin/manage_task/solution_view.html',
        pagination=pagination, page=page)


@admin_bp.route('/score')
def manage_score():
    return render_template('backstage/admin/manage_score.html')


@admin_bp.route('/score/download/teacher', methods=['POST'])
@fresh_login_required
def download_teacher():
    content = render_template('logs/admin/score/download.txt')
    log_user(content)

    com = Competition.current_competition()
    if com.tasks:
        zfile = download_teacher_result(com.id)

        flash(_('The result file is already downloaded.'), 'success')
        return send_file(zfile, as_attachment=True)
    else:
        flash(_('No task.'), 'warning')
        return redirect_back()


@admin_bp.route('/score/download/result', methods=['POST'])
@fresh_login_required
def download_result():
    content = render_template('logs/admin/score/download.txt')
    log_user(content)

    com = Competition.current_competition()
    if com.solutions:
        zfile = download_solution_score(com.id)

        flash(_('The result file is already downloaded.'), 'success')
        return send_file(zfile, as_attachment=True)
    else:
        flash('No solution.', 'warning')
        return redirect_back()
