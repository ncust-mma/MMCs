# -*- coding: utf-8 -*-

from unittest import TestCase

from flask import url_for

from MMCs import create_app
from MMCs.extensions import db
from MMCs.models import User


class BaseTestCase(TestCase):

    def setUp(self):
        app = create_app('testing')
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        db.create_all()

        root_user = User(
            username='root',
            realname='root',
            permission="Root"
        )
        root_user.set_password('test')

        admin_user = User(
            username='admin',
            realname='admin',
            permission="Admin"
        )
        admin_user.set_password('test')

        teacher_user = User(
            username='teacher',
            realname='teacher',
            permission="Teacher"
        )
        teacher_user.set_password('test')

        db.session.add_all([root_user, admin_user, teacher_user])
        db.session.commit()

        self.client.get(url_for('front.set_locale', locale='en_US'))

    def tearDown(self):
        db.drop_all()
        self.context.pop()

    def login(self, username='admin', password='test'):
        return self.client.post(
            url_for('auth.login'),
            data=dict(username=username, password=password),
            follow_redirects=True
        )

    def logout(self):
        return self.client.get(url_for('auth.logout'), follow_redirects=True)
