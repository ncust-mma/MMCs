# -*- coding: utf-8 -*-

from flask import (Blueprint, abort, current_app, flash, redirect,
                   render_template, request, url_for)
from flask_login import current_user, fresh_login_required, login_required

from MMCs.decorators import root_required
from MMCs.extensions import db
from MMCs.forms import (AddUploadFileTypeForm, ButtonChangePasswordForm,
                        ButtonChangeUsernameForm, ButtonEditProfileForm,
                        ChangeUsernameForm, EditProfileForm, RegisterForm,
                        RootChangePasswordForm)
from MMCs.models import UploadFileType, User, StartConfirm, Solution, Task
from MMCs.utils import redirect_back, current_year

root_bp = Blueprint('root', __name__)


@root_bp.route('/')
@login_required
@root_required
def index():
    return redirect(url_for('.manage_competition'))


@root_bp.route('/manage-competition')
@login_required
@root_required
def manage_competition():
    return redirect(url_for('root.behavior'))


@root_bp.route('/manage-competition/behavior', methods=['GET', 'POST'])
@login_required
@root_required
def behavior():
    year = current_year()
    start_flag = StartConfirm.is_existed(year)
    state_flag = StartConfirm.is_start(year)
    return render_template(
        'backstage/root/manage_competition/behavior.html',
        start_flag=start_flag, state_flag=state_flag)


@root_bp.route('/manage-competition/history', methods=['GET', 'POST'])
@login_required
@root_required
def history():
    return render_template(
        'backstage/root/manage_competition/history.html')


@root_bp.route('/manage-competition/behavior/start', methods=['POST'])
@login_required
@root_required
def start_competition():
    year = current_year()
    if StartConfirm.is_existed(year):
        sc = StartConfirm.query.filter_by(year=year).first()
        if sc:
            db.session.delete(sc)

        Solution.query.filter_by(year=year).delete()
        Task.query.filter_by(year=year).delete()
        db.session.commit()
        flash('The year of {} Competition deleted.'.format(year), 'success')

    else:
        sc = StartConfirm(year=year, start_flag=True)
        db.session.add(sc)
        db.session.commit()
        flash('The year of {} Competition start now.'.format(year), 'success')

    return redirect_back()


@root_bp.route('/manage-competition/behavior/switch', methods=['POST'])
@login_required
@root_required
def switch_game_state():
    year = current_year()
    if StartConfirm.is_existed(year):
        sc = StartConfirm.query.filter_by(year=year).first()
        if StartConfirm.is_start(year):
            sc.start_flag = False
        else:
            sc.start_flag = True
        db.session.commit()
        flash('Competition state switched.', 'success')

    else:
        flash('Please start current competition before do it.', 'warning')

    return redirect_back()


@root_bp.route('/manage-personnel/')
@login_required
@root_required
def manage_personnel():
    return redirect(url_for('.personnel_list'))


@root_bp.route('/manage-personnel/personnel-list')
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


@root_bp.route('/manage-personnel/personnel-list/change-password/<int:user_id>', methods=['POST'])
@fresh_login_required
@login_required
@root_required
def personnel_list_change_password(user_id):
    change_password_form = ButtonChangePasswordForm()
    if change_password_form.validate_on_submit():
        form = RootChangePasswordForm()
        if form.validate_on_submit():
            user = User.query.get_or_404(user_id)
            user.set_password(form.password.data)
            db.session.commit()

            flash('Password updated.', 'success')
            return redirect(url_for('.personnel_list'))
    else:
        abort(404)

    return render_template(
        'backstage/root/manage_personnel/personnel_list_edit.html', form=form)


@root_bp.route('/manage-personnel/personnel-list/edit-profile/<int:user_id>', methods=['POST'])
@fresh_login_required
@login_required
@root_required
def personnel_list_edit_profile(user_id):
    edit_profile_form = ButtonEditProfileForm()
    if edit_profile_form.validate_on_submit():
        user = User.query.get_or_404(user_id)
        form = EditProfileForm()
        if form.validate_on_submit():
            user.realname = form.realname.data
            user.remark = form.remark.data
            db.session.commit()

            flash('Profile updated.', 'success')
            return redirect(url_for('.personnel_list'))

        form.realname.data = user.realname
        form.remark.data = user.remark

    else:
        abort(404)

    return render_template(
        'backstage/root/manage_personnel/personnel_list_edit.html', form=form)


@root_bp.route('/manage-personnel/personnel-list/change-username/<int:user_id>', methods=['POST'])
@fresh_login_required
@login_required
@root_required
def personnel_list_change_username(user_id):
    change_username_form = ButtonChangeUsernameForm()
    if change_username_form.validate_on_submit():
        user = User.query.get_or_404(user_id)
        form = ChangeUsernameForm()
        if form.validate_on_submit():
            user.username = form.username.data
            db.session.commit()

            flash('Account registered.', 'success')
            return redirect(url_for('.personnel_list'))

        form.username.data = user.username
        form.username2.data = user.username

    else:
        abort(404)

    return render_template(
        'backstage/root/manage_personnel/personnel_list_edit.html', form=form)


@root_bp.route('/manage-personnel/register', methods=['GET', 'POST'])
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
        flash('Account registered.', 'success')
        return redirect_back()

    return render_template('backstage/root/manage_personnel/register.html', form=form)


# @root_bp.route('/system-settings', methods=['GET', 'POST'])
@login_required
@root_required
def system_settings():
    page = request.args.get('page', 1, type=int)
    current_app.config['USER_PER_PAGE'] = 10
    per_page = current_app.config['FILETYPE_PER_PAGE']
    pagination = UploadFileType.query.order_by(
        UploadFileType.id.desc()).paginate(page, per_page)
    file_types = pagination.items

    form = AddUploadFileTypeForm()
    if form.validate_on_submit():
        ft = UploadFileType(file_type=form.file_type.data)
        db.session.add(ft)
        db.session.commit()
        flash('Upload file type added.', 'success')
        return redirect_back()

    return render_template('backstage/root/system_settings.html', form=form, pagination=pagination, file_types=file_types, page=page, per_page=per_page)


@root_bp.route('/delete/user/<int:user_id>', methods=['POST'])
@login_required
@root_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    flash('User deleted.', 'info')

    return redirect_back()


@root_bp.route('/delete/file-type/<int:file_type_id>', methods=['POST'])
@login_required
@root_required
def delete_file_type(file_type_id):
    file_type = UploadFileType.query.get_or_404(file_type_id)

    db.session.delete(file_type)
    db.session.commit()

    flash('File type deleted.', 'info')

    return redirect_back()
