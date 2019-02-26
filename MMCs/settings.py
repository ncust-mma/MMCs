# -*- coding: utf-8 -*-

import os
import sys
import uuid

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
    SOLUTION_PER_PAGE = 10
    FILETYPE_PER_PAGE = 30

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    CKEDITOR_ENABLE_CSRF = True

    TEACHER_EDIT_TIMES = 1

    BOOTSTRAP_SERVE_LOCAL = True

    UPLOAD_PATH = os.path.join(basedir, 'uploads')
    # file size exceed to 17 Mb will return a 413 error response.
    MAX_CONTENT_LENGTH = 17 * 1024 * 1024
    SOLUTION_SAVE_PATH = os.path.join(UPLOAD_PATH, 'solutions')

    DROPZONE_MAX_FILE_SIZE = MAX_CONTENT_LENGTH
    DROPZONE_MAX_FILES = 20
    DROPZONE_ALLOWED_FILE_CUSTOM = True
    DROPZONE_ENABLE_CSRF = True
    DROPZONE_ALLOWED_FILE_TYPE = '.pdf, .doc, docx'

    ALLOWED_SOLUTION_EXTENSIONS = ['pdf', 'doc', 'docx']


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')
    REDIS_URL = "redis://localhost"


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database


class ProductionConfig(BaseConfig):
    SECRET_KEY = os.getenv('SECRET_KEY', uuid.uuid4().hex)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
