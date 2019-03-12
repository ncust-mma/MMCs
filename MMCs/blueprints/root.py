# -*- coding: utf-8 -*-

import os
from uuid import uuid4

import pandas as pd
from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, send_file, url_for)
from flask_babel import _
from flask_login import current_user, fresh_login_required, login_required

from MMCs.decorators import root_required
from MMCs.extensions import db
from MMCs.forms import (ButtonChangePasswordForm, ButtonChangeUsernameForm,
                        ButtonEditProfileForm, ChangeUsernameForm,
                        CompetitionSettingForm, EditProfileForm,
                        NoticeEditForm, RegisterForm, RootChangePasswordForm)
from MMCs.models import Competition, Solution, Task, User
from MMCs.settings import basedir
from MMCs.utils import redirect_back

root_bp = Blueprint('root', __name__)


@root_bp.route('/')
@login_required
@root_required
def index():
    return redirect(url_for('.manage_competition'))


@root_bp.route('/competition')
@login_required
@root_required
def manage_competition():
    return redirect(url_for('root.behavior'))


@root_bp.route('/competition/behavior')
@login_required
@root_required
def behavior():
    return render_template(
        'backstage/root/manage_competition/behavior.html')


@root_bp.route('/competition/history')
@login_required
@root_required
def history():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['COMPETITION_PER_PAGE']
    pagination = Competition.query.order_by(
        Competition.id.desc()).paginate(page, per_page)
    coms = pagination.items

    return render_template(
        'backstage/root/manage_competition/history.html',
        coms=coms, per_page=per_page, pagination=pagination, page=page)


@root_bp.route('/competition/notice', methods=['GET', 'POST'])
@fresh_login_required
@login_required
@root_required
def notice():
    form = NoticeEditForm()
    if form.validate_on_submit():
        path = os.path.join(
            basedir, current_app.name, 'templates', 'backstage/notice.html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(form.notice.data)

    form.notice.data = render_template('backstage/notice.html')
    return render_template(
        'backstage/root/manage_competition/notice.html', form=form)


@root_bp.route('/competition/settings', methods=['GET', 'POST'])
@fresh_login_required
@login_required
@root_required
def competition_settings():
    form = CompetitionSettingForm()
    if form.validate_on_submit():
        current_app.config['SOLUTION_TASK_NUMBER'] = form.solution_task_number.data
        current_app.config['USER_PER_PAGE'] = form.user_per_page.data
        current_app.config['SOLUTION_PER_PAGE'] = form.solution_per_page.data
        current_app.config['COMPETITION_PER_PAGE'] = form.competition_per_page.data
        current_app.config['DROPZONE_MAX_FILES'] = form.dropzone_max_files.data

    form.solution_task_number.data = current_app.config['SOLUTION_TASK_NUMBER']
    form.user_per_page.data = current_app.config['USER_PER_PAGE']
    form.solution_per_page.data = current_app.config['SOLUTION_PER_PAGE']
    form.competition_per_page.data = current_app.config['COMPETITION_PER_PAGE']
    form.dropzone_max_files.data = current_app.config['DROPZONE_MAX_FILES']

    return render_template(
        'backstage/root/manage_competition/notice.html', form=form)


@root_bp.route('/competition/behavior/start', methods=['POST'])
@fresh_login_required
@login_required
@root_required
def start_competition():
    com = Competition(flag=True)
    db.session.add(com)
    db.session.commit()
    flash(_('A new competition start now.'), 'success')

    return redirect_back()


@root_bp.route('/competition/behavior/switch', methods=['POST'])
@fresh_login_required
@login_required
@root_required
def switch_state():
    com = Competition.current_competition()
    if com:
        if Competition.is_start():
            com.flag = False
            flash(_('Competition stopped.'), 'success')
        else:
            com.flag = True
            flash(_('Competition continued.'), 'success')
        db.session.commit()
    else:
        flash(_('Please start current competition before do it.'), 'warning')

    return redirect_back()


@root_bp.route('/personnel')
@login_required
@root_required
def manage_personnel():
    return redirect(url_for('.personnel_list'))


@root_bp.route('/personnel/list')
@login_required
@root_required
def personnel_list():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['USER_PER_PAGE']
    pagination = User.query.order_by(
        User.id.desc()).paginate(page, per_page)
    users = pagination.items

    edit_profile_form = ButtonEditProfileForm()
    change_username_form = ButtonChangeUsernameForm()
    change_password_form = ButtonChangePasswordForm()

    return render_template(
        'backstage/root/manage_personnel/personnel_list.html',
        pagination=pagination, users=users, page=page, per_page=per_page,
        edit_profile_form=edit_profile_form,
        change_username_form=change_username_form,
        change_password_form=change_password_form)


@root_bp.route('/personnel/list/change-password/<int:user_id>', methods=['POST'])
@fresh_login_required
@login_required
@root_required
def change_password(user_id):
    change_password_form = ButtonChangePasswordForm()
    if change_password_form.validate_on_submit():
        form = RootChangePasswordForm()
        if form.validate_on_submit():
            user = User.query.get_or_404(user_id)
            user.set_password(form.password.data)
            db.session.commit()

            flash(_('Password updated.'), 'success')
            return redirect(url_for('.personnel_list'))
    else:
        abort(404)

    return render_template(
        'backstage/root/manage_personnel/personnel_list_edit.html', form=form)


@root_bp.route('/personnel/list/edit-profile/<int:user_id>', methods=['POST'])
@fresh_login_required
@login_required
@root_required
def edit_profile(user_id):
    edit_profile_form = ButtonEditProfileForm()
    if edit_profile_form.validate_on_submit():
        user = User.query.get_or_404(user_id)
        form = EditProfileForm()
        if form.validate_on_submit():
            user.realname = form.realname.data
            user.remark = form.remark.data
            db.session.commit()

            flash(_('Profile updated.'), 'success')
            return redirect(url_for('.personnel_list'))

        form.realname.data = user.realname
        form.remark.data = user.remark

    else:
        abort(404)

    return render_template(
        'backstage/root/manage_personnel/personnel_list_edit.html', form=form)


@root_bp.route('/personnel/list/change-username/<int:user_id>', methods=['POST'])
@fresh_login_required
@login_required
@root_required
def change_username(user_id):
    change_username_form = ButtonChangeUsernameForm()
    if change_username_form.validate_on_submit():
        user = User.query.get_or_404(user_id)
        form = ChangeUsernameForm()
        if form.validate_on_submit():
            user.username = form.username.data
            db.session.commit()

            flash(_('Username updated.'), 'success')
            return redirect(url_for('.personnel_list'))

        form.username.data = user.username
        form.username2.data = user.username

    else:
        abort(404)

    return render_template(
        'backstage/root/manage_personnel/personnel_list_edit.html', form=form)


@root_bp.route('/personnel/register', methods=['GET', 'POST'])
@fresh_login_required
@login_required
@root_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            realname=form.realname.data,
            permission=form.permission.data,
            remark=form.remark.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Account registered.'), 'success')
        return redirect_back()

    return render_template('backstage/root/manage_personnel/register.html', form=form)


@root_bp.route('/delete/user/<int:user_id>', methods=['POST'])
@fresh_login_required
@login_required
@root_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    flash(_('User deleted.'), 'info')

    return redirect_back()


@root_bp.route('/score/download/<int:competition_id>/teacher', methods=['POST'])
@fresh_login_required
@login_required
@root_required
def download_teacher(competition_id):
    com = Competition.query.get_or_404(competition_id)
    if com.tasks:
        teachers = User.teachers()
        teacher_dic = {teacher.id: (teacher.username, teacher.realname)
                       for teacher in teachers}
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

        return send_file(file, as_attachment=True)
    else:
        flash('No task.', 'warning')
        return redirect_back()


@root_bp.route('/score/download/<int:competition_id>/result', methods=['POST'])
@fresh_login_required
@login_required
@root_required
def download_result(competition_id):
    com = Competition.query.get_or_404(competition_id)
    solutions = com.solutions
    if solutions:
        for solution in solutions:
            tasks = solution.tasks
            solution.score = (
                sum([task.score for task in tasks if task.score]) / len(tasks))
            try:
                db.session.commit()
            except:
                db.session.rollback()

        df = pd.read_sql_query(
            Solution.query.filter_by(competition_id=com.id).statement, db.engine)
        df['index'] = (df['name'].apply(lambda x: x.split('_')[0]))
        df['problem'] = (df['name'].apply(lambda x: x.split('_')[1]))
        df['team_number'] = (df['name'].apply(lambda x: x.split('_')[2]))
        df['team_player'] = (
            df['name'].apply(lambda x: '_'.join(x.split('_')[3:])))

        del df['competition_id']

        file = os.path.join(
            current_app.config['FILE_CACHE_PATH'], uuid4().hex+'.xlsx')
        df.to_excel(file, index=False)

        return send_file(file, as_attachment=True)
    else:
        flash('No solution.', 'warning')
        return redirect_back()
