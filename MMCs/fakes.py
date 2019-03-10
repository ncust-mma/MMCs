# -*- coding: utf-8 -*-

from faker import Faker
from sqlalchemy.sql.expression import func

from MMCs import db
from MMCs.models import Solution, Competition, Task, User
from MMCs.utils import new_filename

fake = Faker()
fake_zh = Faker('zh_CN')


def fake_root():
    user = User(
        username='root',
        realname=fake_zh.name(),
        permission="Root",
        remark=fake_zh.text(),
    )
    user.set_password('mmcs4sxjm')
    db.session.add(user)
    db.session.commit()


def fake_admin():
    user = User(
        username='admin',
        realname=fake_zh.name(),
        permission="Admin",
        remark=fake_zh.text(),
    )
    user.set_password('mmcs4sxjm')
    db.session.add(user)
    db.session.commit()


def fake_default_teacher():
    user = User(
        username='teacher',
        realname=fake_zh.name(),
        permission="Teacher",
        remark=fake_zh.text(),
    )
    user.set_password('mmcs4sxjm')

    db.session.add(user)
    db.session.commit()


def fake_teacher(count=10):
    for _ in range(count):
        user = User(
            username=fake_zh.user_name(),
            realname=fake_zh.name(),
            permission="Teacher",
            remark=fake_zh.text(),
        )
        user.set_password('mmcs4sxjm')

        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()


def fake_solution(count=30):
    for _ in range(count):
        name = '2019_{}_{}_{}_{}_{}.pdf'.format(
            fake.random_element(elements=('A', 'B', 'C', 'D')),
            fake.random_int(min=0, max=999),
            fake_zh.name(), fake_zh.name(), fake_zh.name())
        filename, uuid = new_filename(name)
        solution = Solution(name=filename, uuid=uuid, competition_id=1)

        db.session.add(solution)
        try:
            db.session.commit()
        except:
            db.session.rollback()


def fake_competition():
    com = Competition()
    db.session.add(com)
    db.session.commit()


def fake_task():
    for solution in Solution.query.filter_by(competition_id=1).all():
        for teacher in User.query.filter_by(permission='Teacher').order_by(func.random()).limit(3).all():
            task = Task(
                teacher_id=teacher.id,
                solution_id=solution.id,
                competition_id=1
            )

            db.session.add(task)
            try:
                db.session.commit()
            except:
                db.session.rollback()
