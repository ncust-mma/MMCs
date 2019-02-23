# -*- coding: utf-8 -*-

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from MMCs.extensions import db, whooshee


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True,
                         index=True, nullable=False)
    realname = db.Column(db.String(30), nullable=False)
    permission = db.Column(db.String(10), nullable=False, default='Teacher')
    remark = db.Column(db.Text)
    password_hash = db.Column(db.String(128), nullable=False)

    solutions = db.relationship(
        'Solutions', cascade='save-update, merge, delete')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_teacher(self):
        return self.permission == 'Teacher'

    @property
    def is_admin(self):
        return self.permission == 'Admin'

    @property
    def is_root(self):
        return self.permission == 'Root'


class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    uuid = db.Column(db.String, index=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    teachers = db.relationship(
        'Teachers', cascade='save-update, merge, delete')


class Distribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(
        db.Integer, db.ForeignKey('user.id'))
    solution_uuid = db.Column(db.Integer, db.ForeignKey('solution.uuid'))
    point = db.Column(db.Integer)
    times = db.Column(db.Integer, default=0)
    year = db.Column(db.Integer, nullable=False)

    @property
    def is_able(self):
        return True if self.times < current_app.config['TEACHER_POINT_TIMES'] else False


class StartConfirm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=True, index=True, nullable=False)
    is_start = db.Column(db.Boolean, default=False)
