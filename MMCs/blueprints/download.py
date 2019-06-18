# -*- coding: utf-8 -*-

import os
from uuid import uuid4

import pandas as pd
from flask import Blueprint, abort, current_app, flash, send_file
from flask_babel import _
from flask_login import current_user, fresh_login_required, login_required

from MMCs.decorators import root_required
from MMCs.extensions import db
from MMCs.models import Competition, Log, Solution, Task, User
from MMCs.settings import basedir
from MMCs.utils.link import redirect_back
from MMCs.utils.zip import zip2here

download_bp = Blueprint('download', __name__)


@download_bp.before_request
@fresh_login_required
@login_required
def login_protect():
    pass


@download_bp.route('/competition/<int:competition_id>/teacher-result')
def result_teacher(competition_id):
    com = Competition.query.get_or_404(competition_id)
    if com.tasks:
        statement = Task.query.filter_by(competition_id=com.id).statement
        df = pd.read_sql_query(statement, db.engine)

        df['username'] = (
            df['teacher_id'].apply(lambda x: User.query.get(x).username))
        df['realname'] = (
            df['teacher_id'].apply(lambda x: User.query.get(x).realname))
        df['uuid'] = (
            df['solution_id'].apply(lambda x: Solution.query.get(x).uuid))
        df['index'] = (
            df['solution_id'].apply(lambda x: Solution.query.get(x).index))
        df['problem'] = (
            df['solution_id'].apply(lambda x: Solution.query.get(x).problem))
        df['team_number'] = (
            df['solution_id'].apply(lambda x: Solution.query.get(x).team_number))
        df['team_player'] = (
            df['solution_id'].apply(lambda x: '_'.join(Solution.query.get(x).team_player)))

        df.drop(
            columns=['id', 'teacher_id', 'solution_id', 'competition_id'], inplace=True)

        file = os.path.join(
            current_app.config['FILE_CACHE_PATH'], uuid4().hex + '.xlsx')
        df.to_excel(file, index=False)

        zfile = file.replace('.xlsx', '.zip')
        zip2here(file, zfile, diff=True)

        flash(_('The result file is already downloaded.'), 'success')
        res = send_file(
            zfile, as_attachment=True, attachment_filename='teacher result.zip')
    else:
        flash(_('No task.'), 'warning')
        res = redirect_back()

    return res


@download_bp.route('/competition/<int:competition_id>/final-result')
def result_final(competition_id):
    com = Competition.query.get_or_404(competition_id)
    if com.solutions:
        Competition.update_socre(com.id)
        statement = Solution.query.filter_by(competition_id=com.id).statement
        df = pd.read_sql_query(statement, db.engine)

        df['index'] = (df['name'].apply(lambda x: x.split('_')[0]))
        df['problem'] = (df['name'].apply(lambda x: x.split('_')[1]))
        df['team_number'] = (df['name'].apply(lambda x: x.split('_')[2]))
        df['team_player'] = (
            df['name'].apply(lambda x: '_'.join(x.split('_')[3:])))
        df.drop(columns=['id', 'competition_id', 'name'], inplace=True)

        file = os.path.join(
            current_app.config['FILE_CACHE_PATH'], uuid4().hex + '.xlsx')
        df.to_excel(file, index=False)

        zfile = file.replace('.xlsx', '.zip')
        zip2here(file, zfile, diff=True)

        flash(_('The result file is already downloaded.'), 'success')
        res = send_file(
            zfile, as_attachment=True, attachment_filename='final result.zip')
    else:
        flash(_('No solutions.'), 'warning')
        res = redirect_back()

    return res


@download_bp.route('/logs/operation')
@root_required
def logs_operation():
    # transform file type to excel file type from reading database
    df = pd.read_sql_query(Log.query.statement, db.engine)
    df.drop(columns=['id'], inplace=True)

    # write file to local and pack up it
    file = os.path.join(
        current_app.config['FILE_CACHE_PATH'], uuid4().hex + '.xlsx')
    zfile = file.replace('.xlsx', '.zip')
    df.to_excel(file, index=False)
    zip2here(file, zfile, diff=True)

    flash(_('User logs dowdloaded.'), 'info')
    return send_file(zfile, as_attachment=True, attachment_filename='user operation log.zip')


@download_bp.route('/logs/error')
@root_required
def logs_error():
    if os.path.exists(os.path.join(basedir, 'logs', 'MMCs.log')):
        file = os.path.join(
            current_app.config['FILE_CACHE_PATH'], uuid4().hex + '.zip')
        zip2here(os.path.join(basedir, 'logs'), file, diff=True)
        res = send_file(
            file, as_attachment=True, attachment_filename='system error log.zip')
    else:
        flash('No logs.', 'warning')
        res = redirect_back()

    return res


@download_bp.route('/competition/<int:competition_id>/task')
def task(competition_id):
    com = Competition.query.get_or_404(competition_id)
    tasks = [task for task in current_user.tasks if task.competition_id == com.id]
    paths = [os.path.join(current_app.config['SOLUTION_SAVE_PATH'], task.solution_uuid)
             for task in tasks]
    file = os.path.join(
        current_app.config['FILE_CACHE_PATH'], uuid4().hex + '.zip')
    zip2here(paths, file)

    return send_file(file, as_attachment=True, attachment_filename='tasks.zip')


@download_bp.route('/solution/<path:filename>')
def solution(filename):
    if Competition.is_start():
        path = os.path.join(current_app.config['SOLUTION_SAVE_PATH'], filename)
        if os.path.exists(path):
            return send_file(path, as_attachment=True)
        else:
            abort(404)
    else:
        abort(403)
