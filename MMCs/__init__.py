# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler, SMTPHandler

import click
from flask import Flask, Markup, render_template, request, session
from flask_babel import _
from flask_wtf.csrf import CSRFError

from MMCs.blueprints.admin import admin_bp
from MMCs.blueprints.auth import auth_bp
from MMCs.blueprints.backstage import backstage_bp
from MMCs.blueprints.front import front_bp
from MMCs.blueprints.root import root_bp
from MMCs.blueprints.teacher import teacher_bp
from MMCs.extensions import (babel, bootstrap, cache, ckeditor, csrf, db,
                             dropzone, login_manager, scheduler, toolbar)
from MMCs.models import Competition, Log, Solution, Task, User
from MMCs.settings import basedir, config
from MMCs.utils import read_localfile


def create_app(config_name=None):
    """Using flask factory method to create flask app
    """

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
    register_hook(app)

    return app


def register_logging(app):
    """register log for flask
    """

    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] - %(name)s - %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    if not app.debug:
        file_handler = RotatingFileHandler(
            os.path.join(basedir, 'logs/MMCs.log'),
            maxBytes=10 * 1024 * 1024, backupCount=10)
    else:
        file_handler = RotatingFileHandler(
            os.path.join(basedir, 'logs/MMCs-dev.log'),
            maxBytes=10 * 1024 * 1024, backupCount=10)

    file_handler.setFormatter(request_formatter)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    mail_handler = SMTPHandler(
        mailhost=app.config['MAIL_SERVER'],
        fromaddr=app.config['MAIL_USERNAME'],
        toaddrs=app.config['ADMIN_EMAIL'],
        subject='MMCs Application Error',
        credentials=('apikey', app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.INFO)
    mail_handler.setFormatter(request_formatter)
    app.logger.addHandler(mail_handler)


def register_extensions(app):
    """register all extensions for flask
    """

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    dropzone.init_app(app)
    babel.init_app(app)
    cache.init_app(app)
    toolbar.init_app(app)
    scheduler.init_app(app)
    scheduler.start()


def register_blueprints(app):
    """register all views for flask
    """

    app.register_blueprint(front_bp)
    app.register_blueprint(backstage_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(root_bp, url_prefix='/root')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')


def register_errors(app):
    """register all errors for flask
    """

    @app.errorhandler(400)
    def bad_request(e):
        code = 400
        return render_template('errors.html', code=code, info=_('Bad Request')), code

    @app.errorhandler(401)
    def unauthorized(e):
        code = 401
        return render_template('errors.html', code=code, info=_('Unauthorized')), code

    @app.errorhandler(403)
    def forbidden(e):
        code = 403
        return render_template('errors.html', code=code, info=_('Forbidden')), code

    @app.errorhandler(404)
    def page_not_found(e):
        code = 404
        return render_template('errors.html', code=code, info=_('Page Not Found')), code

    @app.errorhandler(405)
    def method_not_allowed(e):
        code = 405
        return render_template('errors.html', code=code, info=_('Method not allowed')), code

    @app.errorhandler(413)
    def too_large(e):
        code = 413
        return render_template('errors.html', code=code, info=_('Upload too large')), code

    @app.errorhandler(500)
    def internal_server_error(e):
        code = 500
        return render_template('errors.html', code=code, info=_('Internal Server Error Explained')), code

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        code = 400
        return render_template('errors.html', code=code, info=_('Handle CSRF Error')), 400


def register_shell_context(app):
    """register shell context for flask
    """

    @app.shell_context_processor
    def make_shell_context():
        return dict(Competition=Competition,
                    db=db, User=User, Task=Task,
                    Solution=Solution, Log=Log)


def register_global_func(app):
    """register function for jinja
    """

    @app.template_global()
    def current_year():
        return datetime.now().year

    @app.template_global()
    def is_start():
        return Competition.is_start()

    @app.template_global()
    def render_text(file):
        path = os.path.join(
            basedir, app.name, app.template_folder, file)

        return read_localfile(path)


def register_commands(app):
    """register command for flask
    """

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
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def init(drop):
        """Initialize MMCs."""

        from MMCs.fakes import fake_root

        if drop:
            click.confirm(
                'This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')

        click.echo('Initializing the database...')
        db.create_all()

        fake_root()
        click.echo('Generating the default root administrator...')

        if os.system('pybabel compile -d MMCs/translations'):
            raise RuntimeError('compile command failed')

        click.echo('Done.')

    @app.cli.command()
    @click.option('--teacher', default=10, help='Quantity of teacher, default is 10.')
    @click.option('--solution', default=30, help='Quantity of solution, default is 30.')
    def forge(teacher, solution):
        """Generate fake data."""

        from MMCs.fakes import fake_root, fake_admin, fake_teacher, fake_solution, fake_competition, fake_task, \
            fake_default_teacher

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

        fake_competition()
        click.echo('Generating the competition...')

        fake_solution(solution)
        click.echo('Generating %d solution...' % solution)

        fake_task()
        click.echo('Generating the task...')

        fake_competition()
        click.echo('Generating the competition...')

        fake_solution(solution)
        click.echo('Generating %d solution...' % solution)

        fake_task()
        click.echo('Generating the task...')

        click.echo('Done.')

    @app.cli.command()
    def gen_root():
        """Generate root user."""
        from MMCs.fakes import fake_root

        fake_root()
        click.echo('Generating the default root administrator...')
        click.echo('Done.')

    @app.cli.command()
    def gen_admin():
        """Generate admin user."""
        from MMCs.fakes import fake_admin

        fake_admin()
        click.echo('Generating the default administrator...')
        click.echo('Done.')

    @app.cli.command()
    def gen_teacher():
        """Generate teacher user."""
        from MMCs.fakes import fake_default_teacher

        fake_default_teacher()
        click.echo('Generating the default teacher...')
        click.echo('Done.')

    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    @click.argument('locale')
    def init(locale):
        """Initialize a new language."""

        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system(
                'pybabel init -i messages.pot -d MMCs/translations -l ' + locale):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')

    @translate.command()
    def update():
        """Update all languages."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d MMCs/translations'):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system('pybabel compile -d MMCs/translations'):
            raise RuntimeError('compile command failed')


def register_hook(app):
    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=3)
