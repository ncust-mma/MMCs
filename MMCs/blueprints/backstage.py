# -*- coding: utf-8 -*-

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   url_for, request)
from flask_login import (current_user, fresh_login_required, login_required,
                         logout_user)

from MMCs.decorators import (admin_required, permission_required)
from MMCs.extensions import db
from MMCs.forms import ChangePasswordForm, EditProfileForm
from MMCs.models import User
from MMCs.settings import Operations
from MMCs.utils import (flash_errors, generate_token, redirect_back,
                        validate_token)

backstage_bp = Blueprint('backstage', __name__)


@backstage_bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.realname = form.realname.data
        current_user.remark = form.remark.data
        db.session.commit()

        flash('Profile updated.', 'success')
        return redirect(url_for('front.index', username=current_user.username))

    form.username.data = current_user.username
    form.realname.data = current_user.realname
    form.remark.data = current_user.remark

    return render_template('backstage/settings/edit_profile.html', form=form)


@backstage_bp.route('/settings/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.validate_password(form.old_password.data):
            current_user.set_password(form.password.data)
            db.session.commit()
            flash('Password updated.', 'success')
            return redirect(url_for('front.index', username=current_user.username))
        else:
            flash('Old password is incorrect.', 'warning')
    return render_template('backstage/settings/change_password.html', form=form)
