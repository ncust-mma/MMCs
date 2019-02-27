# -*- coding: utf-8 -*-

import os

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, send_file, url_for)
from flask_login import login_required


from MMCs.decorators import admin_required
from MMCs.extensions import db
from MMCs.forms import AdminAddTaskForm
from MMCs.models import Solution, StartConfirm, Task, User
from MMCs.utils import allowed_file, current_year, redirect_back, new_filename

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
@admin_required
def index():
    year = current_year()
    tasks = Task.query.filter(Task.year == year).all()
    teacher_ids = set(i.teacher_id for i in tasks)

    finished_count = 0
    for teacher_id in teacher_ids:
        finished_count += len(User.query.get(teacher_id).finished_task(year))

    progress = finished_count/len(tasks)*100

    return render_template('backstage/admin/overview.html', progress=progress)


@admin_bp.route('/manage-solution/')
@login_required
@admin_required
def manage_solution():
    return redirect(url_for('admin.solution_list'))


@admin_bp.route('/manage-solution/solution-list')
@login_required
@admin_required
def solution_list():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SOLUTION_PER_PAGE']
    pagination = Solution.query.order_by(
        Solution.id.desc()).paginate(page, per_page)
    solutions = pagination.items

    return render_template(
        'backstage/admin/manage_solution/solution_list.html',
        pagination=pagination, solutions=solutions,
        page=page, per_page=per_page)


@admin_bp.route('/manage-solution/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload():
    if request.method == 'POST' and 'file' in request.files:
        year = current_year()
        if StartConfirm.is_start(year):
            file = request.files.get('file')
            filename, uuid = new_filename(file.filename)
            if allowed_file(filename):
                path = os.path.join(
                    current_app.config['SOLUTION_SAVE_PATH'],
                    str(year), uuid)
                solution = Solution(name=filename, uuid=uuid, year=year)
                db.session.add(solution)
                db.session.commit()
                file.save(path)
            else:
                ext = current_app.config['ALLOWED_SOLUTION_EXTENSIONS']
                return '{} only!'.format(', '.join(ext)), 400
        else:
            return "Competition of current year don't start.", 403

    return render_template('backstage/admin/manage_solution/upload.html')


@admin_bp.route('/manage-solution/solution/delete/<int:solution_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_solution_task(solution_id):
    solution = Solution.query.get_or_404(solution_id)

    db.session.delete(solution)
    db.session.commit()

    flash('Solution deleted.', 'info')
    return redirect_back()


@admin_bp.route('/manage-task')
@login_required
@admin_required
def manage_task():
    return redirect(url_for('admin.method_manual'))


@admin_bp.route('/manage-task/method', methods=['GET', 'POST'])
@login_required
@admin_required
def method():
    # TODO: 随机分配

    return render_template('backstage/admin/manage_task/method.html')


@admin_bp.route('/manage-task/method/random')
@login_required
@admin_required
def method_random():

    flash('Randomly assigned.', 'success')
    return redirect_back()


@admin_bp.route('/manage-task/method/manual', methods=['GET', 'POST'])
@login_required
@admin_required
def method_manual():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['USER_PER_PAGE']
    pagination = User.query.filter(User.permission == 'Teacher').order_by(
        User.id.desc()).paginate(page, per_page)
    users = pagination.items

    return render_template(
        'backstage/admin/manage_task/method_manual.html',
        pagination=pagination, users=users, page=page,
        per_page=per_page)


@admin_bp.route('/manage-task/method/manual/check/user/task/<int:user_id>')
@login_required
@admin_required
def check_user(user_id):
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SOLUTION_PER_PAGE']
    pagination = Task.query.filter(
        Task.teacher_id == user_id,
        Task.year == current_year()
    ).order_by(Task.id.desc()).paginate(page, per_page)
    tasks = pagination.items

    return render_template(
        'backstage/admin/manage_task/check.html',
        pagination=pagination, tasks=tasks, page=page, per_page=per_page)


@admin_bp.route('/manage-task/method/manual/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_user_task(user_id):
    for task in Task.query.filter(Task.teacher_id == user_id, Task.year == current_year()):
        db.session.delete(task)
        try:
            db.session.commit()
        except:
            db.session.rollback()

    flash("All tasks of User deleted.", 'success')
    return redirect_back()


@admin_bp.route('/manage-task/method/manual/check/delete/<int:task_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def method_delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()

    flash('Task deleted.', 'success')
    return redirect_back()


@admin_bp.route('/manage-task/method/manual/check/user/solution/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_solution_add_page(user_id):
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SOLUTION_PER_PAGE']

    task_existed = User.query.get(user_id).search_task(current_year())
    solution_existed_ids = set(task.solution_id for task in task_existed)
    pagination = Solution.query.filter(
        ~Solution.id.in_(map(str, solution_existed_ids)),
        Solution.year == current_year()
    ).order_by(Solution.id.desc()).paginate(page, per_page)
    solutions = pagination.items

    form = AdminAddTaskForm()
    if form.validate_on_submit():
        user = User.query.get(user_id)
        solution = Solution.query.get(form.id.data)
        task = Task(
            teacher_id=user.id,
            solution_uuid=solution.uuid,
            year=current_year()
        )
        db.session.add(task)
        db.session.commit()

        flash('Added successed.', 'success')
        return redirect_back()

    return render_template(
        'backstage/admin/manage_task/add.html',
        pagination=pagination, solutions=solutions,
        page=page, per_page=per_page, form=form)


@admin_bp.route('/manage-score')
@login_required
@admin_required
def manage_score():
    return render_template('backstage/admin/manage_score.html')
