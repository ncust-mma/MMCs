# -*- coding: utf-8 -*-

import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from MMCs.extensions import db


class User(db.Model, UserMixin):
    """User table
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(20), unique=True,
        index=True, nullable=False)
    realname = db.Column(db.String(20), nullable=False)
    permission = db.Column(db.String(10), nullable=False, default='Teacher')
    remark = db.Column(db.Text)
    password_hash = db.Column(db.String(128), nullable=False)
    locale = db.Column(db.String(20), default='zh_Hans_CN')

    tasks = db.relationship('Task', cascade='all, delete-orphan')

    def set_password(self, password):
        """Set pwd for current user
        """

        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """Validate current user's pwd
        """

        return check_password_hash(self.password_hash, password)

    @classmethod
    def teachers(self):
        """Return all teachers
        """

        return User.query.filter_by(permission='Teacher').all()

    @property
    def is_teacher(self):
        """Check current user is teacher or not
        """

        return self.permission == 'Teacher'

    @property
    def is_admin(self):
        """Check current user is admin or not
        """

        return self.permission == 'Admin'

    @property
    def is_root(self):
        """Check current user is root or not
        """

        return self.permission == 'Root'

    def can(self, permission_name):
        return self.permission == permission_name

    @property
    def current_all_tasks(self):
        """Return current competition all tasks
        """

        com = Competition.current_competition()
        return [task for task in self.tasks if task.competition_id == com.id]

    @property
    def current_finished_task(self):
        """Return current competition all tasks which have socre
        """

        com = Competition.current_competition()
        return [task for task in self.tasks
                if task.score is not None and task.competition_id == com.id]

    @property
    def current_task_problems(self):
        """Return current competition all problem number
        """

        com = Competition.current_competition()
        current_tasks = self.current_all_tasks

        task_problem_dic = {}
        for task in current_tasks:
            task_problem_dic[task.problem] = (
                task_problem_dic.get(task.problem, 0) + 1)

        for problem in com.problems:
            task_problem_dic[problem] = task_problem_dic.get(problem, 0)

        return task_problem_dic


class Solution(db.Model):
    """Solution table
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    uuid = db.Column(db.String, index=True, nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'))
    score = db.Column(db.Float)

    tasks = db.relationship('Task', cascade='all, delete-orphan')

    @property
    def index(self):
        """return index number
        """

        return self.name.split('_')[0]

    @property
    def problem(self):
        """return problem number
        """

        return self.name.split('_')[1].upper()

    @property
    def team_number(self):
        """return team number
        """

        return self.name.split('_')[2]

    @property
    def team_player(self):
        """return team player name
        """

        return self.name.split('_')[3:]

    @property
    def date(self):
        """return competition date
        """

        return Competition.query.get(self.competition_id).date

    @property
    def finished_task(self):
        com = Competition.current_competition()
        return [task for task in self.tasks
                if task.score is not None and task.competition_id == com.id]


class Task(db.Model):
    """Task table
    """

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    solution_id = db.Column(db.Integer, db.ForeignKey('solution.id'))
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'))
    score = db.Column(db.Float)
    remark = db.Column(db.Text)

    @property
    def solution_uuid(self):
        """Return uuid
        """

        return Solution.query.get(self.solution_id).uuid

    @property
    def filename(self):
        """Return solution filename
        """

        return Solution.query.get(self.solution_id).name

    @property
    def date(self):
        """Return competition date
        """

        return Solution.query.get(self.solution_id).date

    @property
    def problem(self):
        """Return solution problem number
        """

        return Solution.query.get(self.solution_id).problem

    @property
    def team_number(self):
        """Return solution team number
        """

        return Solution.query.get(self.solution_id).team_number


class Competition(db.Model):
    """Competition table
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    date = db.Column(db.Date, index=True, nullable=False,
                     default=datetime.date.today)
    flag = db.Column(db.Boolean, default=False)

    tasks = db.relationship('Task', cascade='all, delete-orphan')
    solutions = db.relationship('Solution', cascade='all, delete-orphan')

    @classmethod
    def current_competition(self):
        """Return current competition
        """

        return Competition.query.order_by(Competition.id.desc()).first()

    @classmethod
    def is_start(self):
        """Check current competition is start or not
        """

        com = Competition.query.order_by(Competition.id.desc()).first()
        return com.flag if com else False

    @property
    def problems(self):
        """Return current competition problems
        """

        return set(solution.problem for solution in self.solutions)

    @classmethod
    def update_socre(self, com_id):
        com = Competition.query.get_or_404(com_id)
        solutions = com.solutions
        if solutions:
            for solution in solutions:
                tasks = solution.tasks
                solution.score = (
                    sum([task.score for task in tasks if task.score is not None]) / len(tasks))
                try:
                    db.session.commit()
                except:
                    db.session.rollback()


class Log(db.Model):
    """User operation log
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip = db.Column(db.String(128))
    time = db.Column(db.DateTime, index=True, default=datetime.datetime.now)

    content = db.Column(db.Text)

    @property
    def permission(self):
        return User.query.get(self.user_id).permission

    @property
    def username(self):
        return User.query.get(self.user_id).username

    @property
    def realname(self):
        return User.query.get(self.user_id).realname
