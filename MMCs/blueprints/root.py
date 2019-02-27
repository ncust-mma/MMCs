# -*- coding: utf-8 -*-

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, fresh_login_required, login_required

from MMCs.decorators import root_required
from MMCs.extensions import db
from MMCs.forms import (AddUploadFileTypeForm, ChangeUsernameForm,
                        EditProfileForm, RegisterForm, RootChangePasswordForm)
from MMCs.models import UploadFileType, User
from MMCs.utils import flash_errors, redirect_back

root_bp = Blueprint('root', __name__)


@root_bp.route('/')
@login_required
@root_required
def index():
    return redirect(url_for('.manage_competition'))


@root_bp.route('/manage-competition', methods=['GET', 'POST'])
@login_required
@root_required
def manage_competition():
    return render_template('backstage/root/manage_competition.html')


@root_bp.route('/competition/start', methods=['GET', 'POST'])
@login_required
@root_required
def start_competition():
    return redirect_back()


@root_bp.route('/competition/state/switch', methods=['GET', 'POST'])
@login_required
@root_required
def switch_game_state():
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

    return render_template(
        'backstage/root/manage_personnel/personnel_list.html',
        pagination=pagination, users=users, page=page, per_page=per_page)


@root_bp.route('/manage-personnel/personnel-list/change-password/<int:user_id>', methods=['GET', 'POST'])
@fresh_login_required
@login_required
@root_required
def personnel_list_change_password(user_id):
    form = RootChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.get(user_id)
        user.set_password(form.password.data)
        db.session.commit()

        flash('Password updated.', 'success')
        return redirect(url_for('.personnel_list'))

    return render_template(
        'backstage/root/manage_personnel/personnel_list_edit.html', form=form)


@root_bp.route('/manage-personnel/personnel-list/edit-profile/<int:user_id>', methods=['GET', 'POST'])
@fresh_login_required
@login_required
@root_required
def personnel_list_edit_profile(user_id):
    user = User.query.get(user_id)
    form = EditProfileForm()
    if form.validate_on_submit():
        user.realname = form.realname.data
        user.remark = form.remark.data
        db.session.commit()

        flash('Profile updated.', 'success')
        return redirect(url_for('.personnel_list'))

    form.realname.data = user.realname
    form.remark.data = user.remark

    flash_errors(form)
    return render_template(
        'backstage/root/manage_personnel/personnel_list_edit.html', form=form)


@root_bp.route('/manage-personnel/personnel-list/change-username/<int:user_id>', methods=['GET', 'POST'])
@fresh_login_required
@login_required
@root_required
def personnel_list_change_username(user_id):
    user = User.query.get(user_id)
    form = ChangeUsernameForm()
    if form.validate_on_submit():
        user.username = form.username.data
        db.session.commit()

        flash('Account registered.', 'success')
        return redirect(url_for('.personnel_list'))

    form.username.data = user.username
    form.username2.data = user.username

    flash_errors(form)
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

    flash_errors(form)
    return render_template('backstage/root/manage_personnel/register.html', form=form)


@root_bp.route('/system-settings', methods=['GET', 'POST'])
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

    flash_errors(form)
    return render_template('backstage/root/system_settings.html', form=form, pagination=pagination, file_types=file_types, page=page, per_page=per_page)


@root_bp.route('/delete/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@root_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    flash('User deleted.', 'info')

    return redirect_back()


@root_bp.route('/delete/file-type/<int:file_type_id>', methods=['GET', 'POST'])
@login_required
@root_required
def delete_file_type(file_type_id):
    file_type = UploadFileType.query.get_or_404(file_type_id)

    db.session.delete(file_type)
    db.session.commit()

    flash('File type deleted.', 'info')

    return redirect_back()
