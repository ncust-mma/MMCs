# -*- coding: utf-8 -*-

from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_dropzone import Dropzone
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_whooshee import Whooshee
from flask_wtf import CSRFProtect

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
ckeditor = CKEditor()
dropzone = Dropzone()
whooshee = Whooshee()


@login_manager.user_loader
def load_user(user_id):
    from MMCs.models import User
    user = User.query.get(int(user_id))
    return user
