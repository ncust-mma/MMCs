# -*- coding: utf-8 -*-

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from MMCs.extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True,
                         index=True, nullable=False)
    realname = db.Column(db.String(20), nullable=False)
    permission = db.Column(db.String(10), nullable=False, default='Teacher')
    remark = db.Column(db.Text)
    password_hash = db.Column(db.String(128), nullable=False)

    tasks = db.relationship(
        'Task', cascade='save-update, merge, delete')

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

    def can(self, permission_name):
        return self.permission == permission_name

    def search_task(self, year):
        return Task.query.filter(Task.teacher_id == self.id, Task.year == year).all()

    def finished_task(self, year):
        return Task.query.filter(
            Task.teacher_id == self.id,
            Task.year == year,
            Task.score != None).all()


class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    uuid = db.Column(db.String, index=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float)

    tasks = db.relationship(
        'Task', cascade='save-update, merge, delete')


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(
        db.Integer, db.ForeignKey('user.id'))
    solution_id = db.Column(db.Integer, db.ForeignKey('solution.id'))
    score = db.Column(db.Float)
    times = db.Column(db.Integer, default=0)
    year = db.Column(db.Integer, nullable=False)

    @property
    def solution_uuid(self):
        return Solution.query.get(self.solution_id).uuid

    @property
    def is_able(self):
        return True if self.times < current_app.config['TEACHER_POINT_TIMES'] else False

    @property
    def filename(self):
        return Solution.query.get(self.solution_id).name


class StartConfirm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=True, index=True, nullable=False)
    start_flag = db.Column(db.Boolean, default=False)

    @classmethod
    def is_start(self, year):
        flag = StartConfirm.query.filter_by(year=year).first()
        return flag.start_flag if flag is not None else False

    @classmethod
    def is_existed(self, year):
        flag = StartConfirm.query.filter_by(year=year).first()
        return True if flag is not None else False


class UploadFileType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_type = db.Column(
        db.String(10), index=True,
        unique=True, nullable=False
    )
