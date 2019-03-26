# -*- coding: utf-8 -*-

import os

from flask import (Blueprint, abort, current_app, flash, render_template,
                   send_file)
from flask_babel import _
from flask_login import current_user, fresh_login_required, login_required

from MMCs.extensions import db
from MMCs.forms import ChangePasswordForm, ChangeUsernameForm, EditProfileForm
from MMCs.models import Competition
from MMCs.utils import log_user, redirect_back

backstage_bp = Blueprint('backstage', __name__)


@backstage_bp.route('/settings/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.realname = form.realname.data
        current_user.remark = form.remark.data
        db.session.commit()

        content = render_template('logs/settings/edit_profile.txt')
        log_user(content)

        flash(_('Profile updated.'), 'success')
        return redirect_back()

    form.realname.data = current_user.realname
    form.remark.data = current_user.remark

    return render_template('backstage/settings/edit_profile.html', form=form)


@backstage_bp.route('/settings/change-username', methods=['GET', 'POST'])
@login_required
@fresh_login_required
def change_username():
    form = ChangeUsernameForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()

        content = render_template('logs/settings/change_username.txt')
        log_user(content)

        flash(_('Username updated.'), 'success')
        return redirect_back()

    return render_template('backstage/settings/change_username.html', form=form)


@backstage_bp.route('/settings/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        content = render_template('logs/settings/change_password.txt')
        log_user(content)

        if current_user.validate_password(form.old_password.data):
            current_user.set_password(form.password.data)
            db.session.commit()

            flash(_('Password updated.'), 'success')
            return redirect_back()
        else:
            flash(_('Old password is incorrect.'), 'warning')

    return render_template('backstage/settings/change_password.html', form=form)


@backstage_bp.route('/solution/<path:filename>')
@login_required
def get_solution(filename):
    content = render_template('logs/download.txt')
    log_user(content)

    if Competition.is_start():
        path = os.path.join(
            current_app.config['SOLUTION_SAVE_PATH'], filename)
        if os.path.exists(path):
            return send_file(path, as_attachment=True)
        else:
            abort(404)
    else:
        abort(403)
