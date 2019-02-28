# -*- coding: utf-8 -*-

import os

import click
from flask import Flask, render_template, request
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError

import logging
from logging.handlers import RotatingFileHandler
from MMCs.blueprints.auth import auth_bp
from MMCs.blueprints.root import root_bp
from MMCs.blueprints.teacher import teacher_bp
from MMCs.blueprints.admin import admin_bp
from MMCs.blueprints.backstage import backstage_bp
from MMCs.blueprints.front import front_bp
from MMCs.extensions import bootstrap, db, login_manager, csrf, ckeditor, dropzone, toolbar
from MMCs.settings import config
from MMCs.models import User, Solution, Task, StartConfirm
from MMCs.utils import current_year, redirect_back


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('MMCs')
    app.config.from_object(config[config_name])

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    register_extensions(app)
    register_blueprints(app)
    register_errors(app)
    register_global_func(app)
    register_commands(app)
    register_shell_context(app)
    register_logging(app)

    return app


def register_logging(app):

    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/MMCs.log'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    if not app.debug:
        app.logger.addHandler(file_handler)


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    dropzone.init_app(app)
    # toolbar.init_app(app)


def register_blueprints(app):
    app.register_blueprint(front_bp)
    app.register_blueprint(backstage_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(root_bp, url_prefix='/root')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html', description=e.description), 400

    @app.errorhandler(401)
    def bad_request(e):
        return render_template('errors/401.html', description=e.description), 401

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html', description=e.description), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html', description=e.description), 404

    @app.errorhandler(405)
    def page_not_found(e):
        return render_template('errors/405.html', description=e.description), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html', description=e.description), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, StartConfirm=StartConfirm,
                    Solution=Solution, Task=Task)


def register_global_func(app):

    @app.template_global()
    def get_current_year():
        return current_year()

    @app.template_global()
    def is_start(year):
        return StartConfirm.is_start(year)

    @app.template_global()
    def redirect2back():
        return redirect_back()


def register_commands(app):

    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm(
                'This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')

        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    def init():
        """Initialize MMCs."""
        click.echo('Initializing the database...')
        db.create_all()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--teacher', default=10, help='Quantity of teacher, default is 10.')
    @click.option('--solution', default=30, help='Quantity of solution, default is 30.')
    @click.option('--filetype', default=5, help='Quantity of filetype, default is 5.')
    def forge(teacher, solution, filetype):
        """Generate fake data."""

        from MMCs.fakes import fake_root, fake_admin, fake_teacher, fake_solution, fake_start_confirm, fake_task, fake_file_type, fake_default_teacher

        db.drop_all()
        db.create_all()

        fake_root()
        click.echo('Generating the default root administrator...')

        fake_admin()
        click.echo('Generating the default administrator...')

        fake_default_teacher()
        click.echo('Generating the default teacher...')

        fake_teacher(teacher)
        click.echo('Generating %d teacher...' % teacher)

        fake_solution(solution)
        click.echo('Generating %d solution...' % solution)

        fake_start_confirm()
        click.echo('Generating the start confirm...')

        fake_task()
        click.echo('Generating the task...')

        fake_file_type()
        click.echo('Generating %d filetype...' % filetype)

        click.echo('Done.')

    @app.cli.command()
    def gen_root():
        """Generate root user."""
        from MMCs.fakes import fake_root

        fake_root()
        click.echo('Generating the root administrator...')
        click.echo('Done.')

    @app.cli.command()
    def gen_admin():
        """Generate admin user."""
        from MMCs.fakes import fake_admin

        fake_admin()
        click.echo('Generating the administrator...')
        click.echo('Done.')
