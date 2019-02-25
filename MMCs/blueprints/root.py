# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required

from MMCs.decorators import root_required
from MMCs.models import User


root_bp = Blueprint('root', __name__)


@root_bp.route('/')
@login_required
@root_required
def index():
    print('here, root.index')
    return redirect(url_for('.competition_management'))


@root_bp.route('/competition_management')
@login_required
@root_required
def competition_management():
    return render_template('backstage/root/competition_management.html')


@root_bp.route('/personnel-management')
@login_required
@root_required
def personnel_management():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = User.query.order_by(User.id.desc()).paginate(page, per_page)
    pagination = User.query.filter(User.id != current_user.id).order_by(
        User.id.desc()).paginate(page, per_page)
    users = pagination.items

    return render_template('backstage/root/personnel_management.html', pagination=pagination, users=users)


@root_bp.route('/system-settings')
@login_required
@root_required
def system_settings():
    return render_template('backstage/root/system_settings.html')
