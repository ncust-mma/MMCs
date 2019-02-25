# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, flash
from flask_login import current_user, fresh_login_required, login_required

from MMCs.extensions import db
from MMCs.forms import ChangePasswordForm, EditProfileForm, ChangeUsernameForm
from MMCs.utils import redirect_back


backstage_bp = Blueprint('backstage', __name__)


@backstage_bp.route('/settings/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.realname = form.realname.data
        current_user.remark = form.remark.data
        db.session.commit()

        flash('Profile updated.', 'success')
        return redirect_back()

    form.realname.data = current_user.realname
    form.remark.data = current_user.remark

    return render_template('backstage/settings/edit_profile.html', form=form)


@backstage_bp.route('/settings/change-username', methods=['GET', 'POST'])
@login_required
def change_username():
    form = ChangeUsernameForm()
    if form.validate_on_submit():
        current_user.set_username(form.username.data)

        flash('Username updated.', 'success')
        return redirect_back()

    form.username.data = current_user.username
    form.username2.data = current_user.username

    return render_template('backstage/settings/change_username.html', form=form)


@backstage_bp.route('/settings/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.validate_password(form.old_password.data):
            current_user.set_password(form.password.data)
            db.session.commit()

            flash('Password updated.', 'success')
            return redirect_back()
        else:
            flash('Old password is incorrect.', 'warning')

    return render_template('backstage/settings/change_password.html', form=form)
