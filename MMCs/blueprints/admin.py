# -*- coding: utf-8 -*-

import os
from uuid import uuid4

import pandas as pd
from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, send_file, url_for)
from flask_babel import _
from flask_login import fresh_login_required, login_required

from MMCs.decorators import admin_required
from MMCs.extensions import db
from MMCs.forms import ButtonAddForm, ButtonCheckForm
from MMCs.models import Competition, Solution, Task, User
from MMCs.utils import (allowed_file, check_filename, new_filename,
                        random_sample, redirect_back, zip2here)

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@admin_required
@login_required
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
@admin_required
@login_required
def manage_solution():
    return redirect(url_for('admin.solution_list'))


@admin_bp.route('/solution/list')
@admin_required
@login_required
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
@admin_required
@login_required
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
                    solution = Solution(
                        name=filename, uuid=uuid, competition_id=com.id)
                    db.session.add(solution)
                    db.session.commit()
                    file.save(os.path.join(path, uuid))
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
@admin_required
@login_required
def delete_solution_task(solution_id):
    solution = Solution.query.get_or_404(solution_id)
    db.session.delete(solution)
    db.session.commit()

    flash(_('Solution deleted.'), 'info')
    return redirect_back()


@admin_bp.route('/task')
@admin_required
@login_required
def manage_task():
    return redirect(url_for('admin.method_manual'))


@admin_bp.route('/task/method', methods=['GET', 'POST'])
@admin_required
@login_required
def method():
    return render_template('backstage/admin/manage_task/method.html')


@admin_bp.route('/task/method/random', methods=['POST'])
@fresh_login_required
@admin_required
@login_required
def method_random():
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


@admin_bp.route('/task/method/manual')
@admin_required
@login_required
def method_manual():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.filter(User.permission == 'Teacher').order_by(
        User.id.desc()).paginate(page, current_app.config['USER_PER_PAGE'])

    check_form = ButtonCheckForm()
    add_form = ButtonAddForm()

    return render_template(
        'backstage/admin/manage_task/manual.html',
        pagination=pagination, page=page,
        check_form=check_form, add_form=add_form)


@admin_bp.route('/task/method/manual/check/<int:user_id>/tasks', methods=['GET', 'POST'])
@admin_required
@login_required
def check_user(user_id):
    com = Competition.current_competition()
    page = request.args.get('page', 1, type=int)

    pagination = Task.query.filter(
        Task.teacher_id == user_id,
        Task.competition_id == com.id
    ).order_by(Task.id.desc()).paginate(page, current_app.config['SOLUTION_PER_PAGE'])

    return render_template(
        'backstage/admin/manage_task/check.html',
        pagination=pagination, page=page)


@admin_bp.route('/task/method/manual/delete/<int:user_id>', methods=['POST'])
@fresh_login_required
@admin_required
@login_required
def delete_user_task(user_id):
    com = Competition.current_competition()
    Task.query.filter(
        Task.teacher_id == user_id,
        Task.competition_id == com.id).delete()
    db.session.commit()

    flash(_("All tasks of User deleted."), 'success')
    return redirect_back()


@admin_bp.route('/task/method/manual/check/delete/<int:task_id>', methods=['POST'])
@fresh_login_required
@admin_required
@login_required
def method_delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash(_('Task deleted.'), 'success')

    return redirect_back()


@admin_bp.route('/task/method/manual/check/<int:user_id>/add', methods=['GET', 'POST'])
@admin_required
@login_required
def task_add_list(user_id):
    page = request.args.get('page', 1, type=int)
    com = Competition.current_competition()
    user = User.query.get_or_404(user_id)
    solution_ids = set(
        task.solution_id for task in user.current_all_tasks)

    pagination = Solution.query.filter(
        ~Solution.id.in_(map(str, solution_ids)),
        Solution.competition_id == com.id
    ).order_by(Solution.id.desc()).paginate(page, current_app.config['SOLUTION_PER_PAGE'])

    return render_template(
        'backstage/admin/manage_task/add.html',
        pagination=pagination, page=page, user_id=user.id)


@admin_bp.route('/task/method/manual/check/<int:user_id>/add/<int:solution_id>', methods=['POST'])
@fresh_login_required
@admin_required
@login_required
def task_add(user_id, solution_id):
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


@admin_bp.route('/score')
@admin_required
@login_required
def manage_score():
    return render_template('backstage/admin/manage_score.html')


@admin_bp.route('/score/download/teacher', methods=['POST'])
@fresh_login_required
@admin_required
@login_required
def download_teacher():
    com = Competition.current_competition()
    if com.tasks:
        teacher_dic = {teacher.id: (teacher.username, teacher.realname)
                       for teacher in User.teachers()}
        solutions = Solution.query.filter_by(competition_id=com.id).all()
        solution_dic = {solution.id: (solution.name,
                                      solution.index,
                                      solution.problem,
                                      solution.team_number,
                                      solution.team_player)
                        for solution in solutions}
        df = pd.read_sql_query(
            Task.query.filter_by(competition_id=com.id).statement, db.engine)

        df['username'] = (
            df['teacher_id'].apply(lambda x: teacher_dic.get(x)[0]))
        df['realname'] = (
            df['teacher_id'].apply(lambda x: teacher_dic.get(x)[1]))

        df['filename'] = (
            df['solution_id'].apply(lambda x: solution_dic.get(x)[0]))
        df['index'] = (
            df['solution_id'].apply(lambda x: solution_dic.get(x)[1]))
        df['problem'] = (
            df['solution_id'].apply(lambda x: solution_dic.get(x)[2]))
        df['team_number'] = (
            df['solution_id'].apply(lambda x: solution_dic.get(x)[3]))
        df['team_player'] = (
            df['solution_id'].apply(lambda x: '_'.join(solution_dic.get(x)[4])))

        del df['teacher_id']
        del df['solution_id']
        del df['competition_id']

        file = os.path.join(
            current_app.config['FILE_CACHE_PATH'], uuid4().hex+'.xlsx')
        df.to_excel(file, index=False)

        zipfile = file.replace('.xlsx', '.zip')
        zip2here(file, zipfile)

        print(zipfile)
        flash(_('The result file is already downloaded.'), 'success')
        return send_file(zipfile, as_attachment=True)
    else:
        flash('No task.', 'warning')
        return redirect_back()


@admin_bp.route('/score/download/result', methods=['POST'])
@fresh_login_required
@admin_required
@login_required
def download_result():
    com = Competition.current_competition()
    solutions = com.solutions
    if solutions:
        for solution in solutions:
            tasks = solution.tasks
            solution.score = (
                sum([task.score for task in tasks if task.score is not None]) / len(tasks))
            try:
                db.session.commit()
            except:
                db.session.rollback()

        df = pd.read_sql_query(
            Solution.query.filter_by(competition_id=com.id).statement, db.engine)
        df['index'] = df['name'].apply(lambda x: x.split('_')[0])
        df['problem'] = df['name'].apply(lambda x: x.split('_')[1])
        df['team_number'] = df['name'].apply(lambda x: x.split('_')[2])
        df['team_player'] = (
            df['name'].apply(lambda x: '_'.join(x.split('_')[3:])))
        del df['competition_id']

        file = os.path.join(
            current_app.config['FILE_CACHE_PATH'], uuid4().hex+'.xlsx')
        df.to_excel(file, index=False)

        zipfile = file.replace('.xlsx', '.zip')
        zip2here(file, zipfile)

        flash(_('The result file is already downloaded.'), 'success')
        return send_file(zipfile, as_attachment=True)
    else:
        flash('No solution.', 'warning')
        return redirect_back()
