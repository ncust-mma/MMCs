# -*- coding: utf-8 -*-

import os
import sys
from uuid import uuid4

from flask_babel import lazy_gettext as _l

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret key')

    USER_PER_PAGE = 30
    SOLUTION_PER_PAGE = 20
    COMPETITION_PER_PAGE = 10

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    CKEDITOR_ENABLE_CSRF = True

    BOOTSTRAP_SERVE_LOCAL = True

    UPLOAD_PATH = os.path.join(basedir, 'uploads')
    # file size exceed to 17 Mb will return a 413 error response.
    MAX_CONTENT_LENGTH = 17 * 1024 * 1024
    SOLUTION_SAVE_PATH = UPLOAD_PATH

    DROPZONE_MAX_FILE_SIZE = MAX_CONTENT_LENGTH
    DROPZONE_MAX_FILES = 20
    DROPZONE_ALLOWED_FILE_CUSTOM = True
    DROPZONE_ENABLE_CSRF = True
    DROPZONE_ALLOWED_FILE_TYPE = '.pdf, .doc, .docx'
    DROPZONE_DEFAULT_MESSAGE = _l('Drop files here or click to upload.')

    ALLOWED_SOLUTION_EXTENSIONS = set(['pdf', 'doc', 'docx'])

    SCORE_UPPER_LIMIT = 100
    SCORE_LOWER_LIMIT = 0

    MMCS_LOCALES = ['zh_Hans_CN', 'en_US']
    BABEL_DEFAULT_LOCALE = MMCS_LOCALES[0]

    SOLUTION_TASK_NUMBER = 3

    MAIL_USE_SSL = True
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT = os.getenv('MAIL_PORT', 587)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

    SENDGRID_DEFAULT_FROM = MAIL_USERNAME
    SENDGRID_API_KEY = MAIL_PASSWORD

    CACHE_TYPE = 'simple'

    FILE_CACHE_PATH = os.path.join(basedir, 'cache')

    SESSION_LIFETIME_MINUTES = int(os.getenv('SESSION_LIFETIME_MINUTES', 10))


class DevelopmentConfig(BaseConfig):
    FLASK_ENV = 'development'
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')
    REDIS_URL = "redis://localhost"


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database


class ProductionConfig(BaseConfig):
    FLASK_ENV = 'production'
    SECRET_KEY = os.getenv('SECRET_KEY', uuid4().hex)
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
