# -*- coding: utf-8 -*-

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_babel import _
from flask_login import (confirm_login, current_user, login_fresh,
                         login_required, login_user, logout_user)

from MMCs.forms.auth import LoginForm
from MMCs.models import User
from MMCs.utils.link import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('front.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.validate_password(form.password.data):
            if login_user(user, form.remember_me.data):

                flash(_('Login success.'), 'info')
                return redirect_back()
        else:
            flash(_('Invalid username or password.'), 'warning')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('Logout success.'), 'info')

    return redirect(url_for('front.index'))


@auth_bp.route('/re-authenticate', methods=['GET', 'POST'])
@login_required
def re_authenticate():
    if login_fresh():
        return redirect(url_for('front.index'))

    form = LoginForm()
    if form.validate_on_submit() and current_user.validate_password(form.password.data):
        confirm_login()

        return redirect_back()
    return render_template('auth/login.html', form=form)
