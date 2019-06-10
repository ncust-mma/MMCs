# -*- coding: utf-8 -*-

import os
from uuid import uuid4

import pandas as pd
from flask import current_app, flash
from flask_babel import _

from MMCs.extensions import db
from MMCs.models import Competition, Log, Solution, Task, User
from MMCs.utils.zip import zip2here


def gen_teacher_result(competition_id):
    """Download one competition all teacher result
    """

    statement = Task.query.filter_by(competition_id=competition_id).statement
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

    return zfile


def gen_solution_score(competition_id):
    """Download one competition all solution result
    """

    Competition.update_socre(competition_id)
    statement = Solution.query.filter_by(
        competition_id=competition_id).statement
    df = pd.read_sql_query(statement, db.engine)

    df['index'] = (df['name'].apply(lambda x: x.split('_')[0]))
    df['problem'] = (df['name'].apply(lambda x: x.split('_')[1]))
    df['team_number'] = (df['name'].apply(lambda x: x.split('_')[2]))
    df['team_player'] = (df['name'].apply(
        lambda x: '_'.join(x.split('_')[3:])))

    df.drop(columns=['id', 'competition_id', 'name'], inplace=True)

    file = os.path.join(
        current_app.config['FILE_CACHE_PATH'], uuid4().hex + '.xlsx')
    df.to_excel(file, index=False)

    zfile = file.replace('.xlsx', '.zip')
    zip2here(file, zfile, diff=True)

    flash(_('The result file is already downloaded.'), 'success')

    return zfile


def download_user_operation():
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
    return zfile
