# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user, login_fresh, confirm_login

from MMCs.extensions import db
from MMCs.forms import LoginForm, RegisterForm, ResetPasswordForm
from MMCs.models import User
from MMCs.settings import Operations
from MMCs.utils import generate_token, validate_token, redirect_back

auth_bp = Blueprint('auth', __name__)
