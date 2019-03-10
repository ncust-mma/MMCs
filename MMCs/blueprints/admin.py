# -*- coding: utf-8 -*-

import os
import random
from uuid import uuid4

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, send_file, url_for)
from flask_babel import _
from flask_login import login_required

import pandas as pd
from MMCs.decorators import admin_required
from MMCs.extensions import db
from MMCs.forms import AdminAddTaskForm, ButtonAddForm, ButtonCheckForm
from MMCs.models import Competition, Solution, Task, User
from MMCs.settings import basedir
from MMCs.utils import (allowed_file, check_filename, new_filename,
                        redirect_back)

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
@admin_required
def index():
    progress = task_number = 0
    if Competition.is_start():
        com = Competition.current_competition()
        tasks = com.tasks
        if tasks:
            finished = [task for task in tasks if task.score]
            progress = len(finished)/len(tasks)*100
            task_number = len(tasks)

    return render_template('backstage/admin/overview.html', progress=progress, task_number=task_number)


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
    com = Competition.current_competition()
    pagination = Solution.query.filter_by(competition_id=com.id).order_by(
        Solution.id.desc()).paginate(page, per_page)
    solutions = pagination.items
    form = ButtonAddForm()

    return render_template(
        'backstage/admin/manage_solution/solution_list.html',
        pagination=pagination, solutions=solutions,
        page=page, per_page=per_page, form=form)


@admin_bp.route('/manage-solution/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload():
    if request.method == 'POST' and 'file' in request.files:
        path = current_app.config['SOLUTION_SAVE_PATH']
        if not os.path.exists(path):
            os.mkdir(path)

        if Competition.is_start():
            file = request.files.get('file')
            filename, uuid = new_filename(file.filename)
            if allowed_file(filename):
                flag, info = check_filename(filename)
                if flag:
                    com = Competition.current_competition()
                    filepath = os.path.join(path, filename)
                    solution = Solution(
                        name=filename, uuid=uuid, competition_id=com.id)
                    db.session.add(solution)
                    db.session.commit()
                    file.save(filepath)
                else:
                    return info, 400
            else:
                ext = current_app.config['ALLOWED_SOLUTION_EXTENSIONS']
                return '{} only!'.format(', '.join(ext)), 400
        else:
            return _("Competition of current year don't start."), 403

    return render_template('backstage/admin/manage_solution/upload.html')


@admin_bp.route('/manage-solution/solution/delete/<int:solution_id>', methods=['POST'])
@login_required
@admin_required
def delete_solution_task(solution_id):
    solution = Solution.query.get_or_404(solution_id)

    db.session.delete(solution)
    db.session.commit()

    flash(_('Solution deleted.'), 'info')
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
    return render_template('backstage/admin/manage_task/method.html')


@admin_bp.route('/manage-task/method/random', methods=['POST'])
@login_required
@admin_required
def method_random():
    com = Competition.current_competition()
    Task.query.filter_by(competition_id=com.id).delete()
    db.session.commit()

    # TODO: 随机分配方案
    samples = current_app.config['MAX_TEACHER_TASK_NUMBER']
    solutions = Solution.query.filter_by(competition_id=com.id).all()
    if solutions:
        teachers = User.query.filter_by(permission='Teacher').all()
        if teachers:
            for solution in solutions:
                for teacher in random.sample(teachers, samples):
                    task = Task(
                        teacher_id=teacher.id,
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


@admin_bp.route('/manage-task/method/manual')
@login_required
@admin_required
def method_manual():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['USER_PER_PAGE']
    pagination = User.query.filter(User.permission == 'Teacher').order_by(
        User.id.desc()).paginate(page, per_page)
    users = pagination.items
    check_form = ButtonCheckForm()
    add_form = ButtonAddForm()

    return render_template(
        'backstage/admin/manage_task/method_manual.html',
        pagination=pagination, users=users, page=page,
        per_page=per_page, check_form=check_form, add_form=add_form)


@admin_bp.route('/manage-task/method/manual/check/user/task/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def check_user(user_id):
    com = Competition.current_competition()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SOLUTION_PER_PAGE']
    pagination = Task.query.filter(
        Task.teacher_id == user_id,
        Task.competition_id == com.id
    ).order_by(Task.id.desc()).paginate(page, per_page)
    tasks = pagination.items
    return render_template(
        'backstage/admin/manage_task/check.html',
        pagination=pagination, tasks=tasks,
        page=page, per_page=per_page)


@admin_bp.route('/manage-task/method/manual/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user_task(user_id):
    com = Competition.current_competition()
    Task.query.filter(
        Task.teacher_id == user_id,
        Task.competition_id == com.id).delete()
    db.session.commit()

    flash(_("All tasks of User deleted."), 'success')
    return redirect_back()


@admin_bp.route('/manage-task/method/manual/check/delete/<int:task_id>', methods=['POST'])
@login_required
@admin_required
def method_delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash(_('Task deleted.'), 'success')

    return redirect_back()


@admin_bp.route('/manage-task/method/manual/check/user/solution/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_solution_add_page(user_id):
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['SOLUTION_PER_PAGE']

    com = Competition.current_competition()
    user = User.query.get_or_404(user_id)
    task_existed = user.search_task()
    solution_existed_ids = set(task.solution_id for task in task_existed)
    pagination = Solution.query.filter(
        ~Solution.id.in_(map(str, solution_existed_ids)),
        Solution.competition_id == com.id
    ).order_by(Solution.id.desc()).paginate(page, per_page)
    solutions = pagination.items

    return render_template(
        'backstage/admin/manage_task/add.html',
        pagination=pagination, solutions=solutions,
        page=page, per_page=per_page, user_id=user.id)


@admin_bp.route('/manage-task/method/manual/check/user/solution/add/<int:user_id>&<int:solution_id>', methods=['POST'])
@login_required
@admin_required
def user_solution_add(user_id, solution_id):
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


@admin_bp.route('/manage-score')
@login_required
@admin_required
def manage_score():
    return render_template('backstage/admin/manage_score.html')


@admin_bp.route('/manage-score/download/teacher', methods=['POST'])
@login_required
@admin_required
def download_teacher():
    path = os.path.join(basedir, 'cache')
    if not os.path.exists(path):
        os.mkdir(path)

    com = Competition.current_competition()
    if com.tasks:
        teachers = User.query.filter_by(permission='Teacher').all()
        teacher_dic = dict((teacher.id, (teacher.username, teacher.realname))
                           for teacher in teachers)
        solutions = Solution.query.filter_by(competition_id=com.id).all()
        solution_dic = dict((solution.id, (solution.name, solution.index,
                                           solution.problem, solution.team_number,
                                           solution.team_player))
                            for solution in solutions)
        df = pd.read_sql_query(
            Task.query.filter_by(competition_id=com.id).statement, db.engine)
        df['username'] = df['teacher_id'].apply(
            lambda x: teacher_dic.get(x)[0])
        df['realname'] = df['teacher_id'].apply(
            lambda x: teacher_dic.get(x)[1])
        df['filename'] = df['solution_id'].apply(
            lambda x: solution_dic.get(x)[0])
        df['index'] = df['solution_id'].apply(lambda x: solution_dic.get(x)[1])
        df['problem'] = df['solution_id'].apply(
            lambda x: solution_dic.get(x)[2])
        df['team_number'] = df['solution_id'].apply(
            lambda x: solution_dic.get(x)[3])
        df['team_player'] = df['solution_id'].apply(
            lambda x: '_'.join(solution_dic.get(x)[4]))

        del df['teacher_id']
        del df['solution_id']
        del df['competition_id']

        file = os.path.join(path, uuid4().hex+'.xlsx')
        df.to_excel(file, index=False)

        return send_file(file, as_attachment=True)
    else:
        flash('No task.', 'warning')
        return redirect_back()


@admin_bp.route('/manage-score/download/result', methods=['POST'])
@login_required
@admin_required
def download_result():
    path = os.path.join(basedir, 'cache')
    if not os.path.exists(path):
        os.mkdir(path)

    com = Competition.current_competition()
    if com.solutions:
        solutions = com.solutions
        for solution in solutions:
            tasks = solution.tasks
            solution.score = sum(
                [task.score for task in tasks if task.score]) / len(tasks)
            try:
                db.session.commit()
            except:
                db.session.rollback()

        df = pd.read_sql_query(
            Solution.query.filter_by(competition_id=com.id).statement, db.engine)
        df['index'] = df['name'].apply(lambda x: x.split('_')[0])
        df['problem'] = df['name'].apply(lambda x: x.split('_')[1])
        df['team_number'] = df['name'].apply(lambda x: x.split('_')[2])
        df['team_player'] = df['name'].apply(
            lambda x: '_'.join(x.split('_')[3:]))

        del df['competition_id']

        file = os.path.join(path, uuid4().hex+'.xlsx')
        df.to_excel(file, index=False)

        return send_file(file, as_attachment=True)
    else:
        flash('No solution.', 'warning')
        return redirect_back()
