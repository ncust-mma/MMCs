# -*- coding: utf-8 -*-

import os
from uuid import uuid4

import pandas as pd
from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, send_file, url_for)
from flask_babel import _
from flask_login import fresh_login_required, login_required

from MMCs.decorators import root_required
from MMCs.extensions import db
from MMCs.forms import (AboutEditForm, AboutImageUploadForm,
                        ButtonChangePasswordForm, ButtonChangeUsernameForm,
                        ButtonEditProfileForm, ChangeUsernameForm,
                        CompetitionSettingForm, EditProfileForm,
                        ErrorImageUploadForm, IndexImageUploadForm,
                        NoticeEditForm, RegisterForm, RootChangePasswordForm)
from MMCs.models import Competition, Solution, Task, User
from MMCs.settings import basedir
from MMCs.utils import flash_errors, redirect_back, zip2here

root_bp = Blueprint('root', __name__)


@root_bp.route('/')
@root_required
@login_required
def index():
    return redirect(url_for('.manage_competition'))


@root_bp.route('/competition')
@root_required
@login_required
def manage_competition():
    return redirect(url_for('root.behavior'))


@root_bp.route('/competition/behavior')
@root_required
@login_required
def behavior():
    return render_template(
        'backstage/root/manage_competition/behavior.html')


@root_bp.route('/competition/history')
@root_required
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    pagination = Competition.query.order_by(
        Competition.id.desc()).paginate(page, current_app.config['COMPETITION_PER_PAGE'])

    return render_template(
        'backstage/root/manage_competition/history.html',
        pagination=pagination, page=page)


@root_bp.route('/competition/notice', methods=['GET', 'POST'])
@fresh_login_required
@root_required
@login_required
def notice():
    form = NoticeEditForm()
    if form.validate_on_submit():
        path = os.path.join(
            basedir, current_app.name, 'templates', 'showing/notice.html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(form.notice.data)

        flash(_('Setting updated.'), 'success')
        return redirect_back()

    form.notice.data = render_template('showing/notice.html')

    return render_template(
        'backstage/root/manage_competition/notice.html', form=form)


@root_bp.route('/competition/settings', methods=['GET', 'POST'])
@fresh_login_required
@root_required
@login_required
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
@root_required
@login_required
def start_competition():
    com = Competition(flag=True)
    db.session.add(com)
    db.session.commit()
    flash(_('A new competition start now.'), 'success')

    return redirect_back()


@root_bp.route('/competition/behavior/switch', methods=['POST'])
@fresh_login_required
@root_required
@login_required
def switch_state():
    com = Competition.current_competition()
    if com:
        if com.is_start():
            com.flag = False
            flash(_('Competition stopped.'), 'success')
        else:
            com.flag = True
            flash(_('Competition continued.'), 'success')
        db.session.commit()
    else:
        flash(_('Please start new competition before do it.'), 'warning')

    return redirect_back()


@root_bp.route('/personnel')
@root_required
@login_required
def manage_personnel():
    return redirect(url_for('.personnel_list'))


@root_bp.route('/personnel/list')
@root_required
@login_required
def personnel_list():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(
        User.id.desc()).paginate(page, current_app.config['USER_PER_PAGE'])

    edit_profile_form = ButtonEditProfileForm()
    change_username_form = ButtonChangeUsernameForm()
    change_password_form = ButtonChangePasswordForm()

    return render_template(
        'backstage/root/manage_personnel/personnel_list.html',
        pagination=pagination, page=page,
        edit_profile_form=edit_profile_form,
        change_username_form=change_username_form,
        change_password_form=change_password_form)


@root_bp.route('/personnel/list/change-password/<int:user_id>', methods=['POST'])
@fresh_login_required
@root_required
@login_required
def change_password(user_id):
    form = ButtonChangePasswordForm()
    if form.change_pwd.data and form.validate_on_submit():
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
@root_required
@login_required
def edit_profile(user_id):
    form = ButtonEditProfileForm()
    if form.edit.data and form.validate_on_submit():
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
@root_required
@login_required
def change_username(user_id):
    form = ButtonChangeUsernameForm()
    if form.change_username.data and form.validate_on_submit():
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
@root_required
@login_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            realname=form.realname.data,
            permission=form.permission.data,
            remark=form.remark.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Account registered.'), 'success')
        return redirect_back()

    return render_template('backstage/root/manage_personnel/register.html', form=form)


@root_bp.route('/delete/user/<int:user_id>', methods=['POST'])
@fresh_login_required
@root_required
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    flash(_('User deleted.'), 'info')

    return redirect_back()


@root_bp.route('/score/download/<int:competition_id>/teacher', methods=['POST'])
@fresh_login_required
@root_required
@login_required
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

        zipfile = file.replace('.xlsx', '.zip')
        zip2here(file, zipfile)

        flash(_('The result file is already downloaded.'), 'success')
        return send_file(zipfile, as_attachment=True)
    else:
        flash('No task.', 'warning')
        return redirect_back()


@root_bp.route('/score/download/<int:competition_id>/result', methods=['POST'])
@fresh_login_required
@root_required
@login_required
def download_result(competition_id):
    com = Competition.query.get_or_404(competition_id)
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
        df['index'] = (df['name'].apply(lambda x: x.split('_')[0]))
        df['problem'] = (df['name'].apply(lambda x: x.split('_')[1]))
        df['team_number'] = (df['name'].apply(lambda x: x.split('_')[2]))
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


@root_bp.route('/settings')
@root_required
@login_required
def system_settings():
    return redirect(url_for('root.logs'))


@root_bp.route('/settings/logs')
@fresh_login_required
@root_required
@login_required
def logs():
    return render_template('backstage/root/manage_settings/logs.html')


@root_bp.route('/settings/logs/download', methods=['POST'])
@fresh_login_required
@root_required
@login_required
def logs_download():
    if os.path.exists(os.path.join(basedir, 'logs', 'MMCs.log')):
        file = os.path.join(
            current_app.config['FILE_CACHE_PATH'], uuid4().hex+'.zip')
        zip2here(os.path.join(basedir, 'logs'), file)

        return send_file(file, as_attachment=True)
    else:
        flash('No logs.', 'warning')
        return redirect_back()


@root_bp.route('/settings/about', methods=['GET', 'POST'])
@fresh_login_required
@root_required
@login_required
def about():
    form = AboutEditForm()
    if form.validate_on_submit():
        path = os.path.join(
            basedir, current_app.name, 'templates', 'showing/about.html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(form.about.data)

        flash(_('Setting updated.'), 'success')
        return redirect_back()

    form.about.data = render_template('showing/about.html')

    return render_template('backstage/root/manage_settings/about.html', form=form)


@root_bp.route('/settings/images', methods=['GET', 'POST'])
@fresh_login_required
@root_required
@login_required
def images():
    index_form = IndexImageUploadForm()
    about_form = AboutImageUploadForm()
    error_form = ErrorImageUploadForm()
    if request.method == 'POST':
        path = os.path.join(basedir, current_app.name, 'static', 'images')
        img = request.files.get('file')
        if index_form.index_upload.data and index_form.validate_on_submit():
            img.save(os.path.join(path, 'index.jpg'))
            flash(_('Image updated.'), 'success')

        if about_form.about_upload.data and about_form.validate_on_submit():
            img.save(os.path.join(path, 'about.jpg'))
            flash(_('Image updated.'), 'success')

        if error_form.error_upload.data and error_form.validate_on_submit():
            img.save(os.path.join(path, 'error.jpg'))
            flash(_('Image updated.'), 'success')

        flash_errors(index_form)
        flash_errors(about_form)
        flash_errors(error_form)

        return redirect_back()

    return render_template(
        'backstage/root/manage_settings/images.html',
        index_form=index_form, about_form=about_form, error_form=error_form)
