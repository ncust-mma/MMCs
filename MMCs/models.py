# -*- coding: utf-8 -*-

from datetime import date

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
    locale = db.Column(db.String(20), default='zh_Hans_CN')

    tasks = db.relationship(
        'Task', cascade='save-update, merge, delete')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def teachers(self):
        return User.query.filter_by(permission='Teacher').all()

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

    def search_task(self):
        com = Competition.current_competition()
        return Task.query.filter(Task.teacher_id == self.id, Task.competition_id == com.id).all()

    def finished_task(self):
        com = Competition.current_competition()
        return Task.query.filter(
            Task.teacher_id == self.id,
            Task.competition_id == com.id,
            Task.score != None).all()


class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    uuid = db.Column(db.String, index=True, nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'))
    score = db.Column(db.Float)

    tasks = db.relationship(
        'Task', cascade='save-update, merge, delete')

    @property
    def index(self):
        return self.name.split('_')[0]

    @property
    def problem(self):
        return self.name.split('_')[1]

    @property
    def team_number(self):
        return self.name.split('_')[2]

    @property
    def team_player(self):
        return self.name.split('_')[3:]

    @property
    def date(self):
        return Competition.query.get(self.competition_id).date


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    solution_id = db.Column(db.Integer, db.ForeignKey('solution.id'))
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'))
    score = db.Column(db.Float)
    remark = db.Column(db.Text)

    @property
    def solution_uuid(self):
        return Solution.query.get(self.solution_id).uuid

    @property
    def is_able(self):
        return True if self.times < current_app.config['TEACHER_POINT_TIMES'] else False

    @property
    def filename(self):
        return Solution.query.get(self.solution_id).name

    @property
    def date(self):
        return Solution.query.get(self.solution_id).date

    @property
    def problem(self):
        return Solution.query.get(self.solution_id).problem

    @property
    def team_number(self):
        return Solution.query.get(self.solution_id).team_number


class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, nullable=False, default=date.today)
    flag = db.Column(db.Boolean, default=False)

    tasks = db.relationship(
        'Task', cascade='save-update, merge, delete')

    solutions = db.relationship(
        'Solution', cascade='save-update, merge, delete')

    @classmethod
    def current_competition(self):
        return Competition.query.order_by(Competition.id.desc()).first()

    @classmethod
    def is_start(self):
        com = Competition.query.order_by(Competition.id.desc()).first()
        return com.flag if com is not None else False

    @classmethod
    def is_existed(self, sid):
        return True if Competition.query.get(sid) is not None else False

    @property
    def problems(self):
        solutions = self.solutions
        return set(solution.problem for solution in solutions)
