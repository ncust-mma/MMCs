# -*- coding: utf-8 -*-

from faker import Faker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import func

from MMCs import db
from MMCs.models import Distribution, Solution, StartConfirm, User

fake = Faker()
fake_zh = Faker('zh_CN')


def fake_root():
    user = User(
        username='root',
        realname='Test for Root',
        permission="Root",
        remark=fake_zh.text(),
    )
    user.set_password('mmcs4test')
    db.session.add(user)
    db.session.commit()


def fake_admin():
    user = User(
        username='admin',
        realname='Test for Admin',
        permission="Admin",
        remark=fake_zh.text(),
    )
    user.set_password('mmcs4test')
    db.session.add(user)
    db.session.commit()


def fake_teacher(count=10):
    for _ in range(count):
        user = User(
            username=fake_zh.user_name(),
            realname='Test for Teacher',
            permission="Teacher",
            remark=fake_zh.text(),
        )
        user.set_password('mmcs4test')

        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_solution(count=30):
    for _ in range(count):
        name = 'NCUST_SXJM{}TEAM_{}_{}_{}_{}.pdf'.format(
            fake.random_int(min=0, max=999),
            fake.random_element(elements=('A', 'B', 'C', 'D')),
            fake_zh.name(), fake_zh.name(), fake_zh.name())
        solution = Solution(year=2019, name=name)
        # name = solution.filter_name(name)
        solution.set_uuid(name)

        db.session.add(solution)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_start_confirm():
    sc = StartConfirm(year=2019)
    db.session.add(sc)
    db.session.commit()


def fake_distribution():
    for solution in Solution.query.filter_by(year=2019).all():
        for teacher in User.query.filter_by(permission='Teacher').order_by(func.random()).limit(3).all():
            distribution = Distribution(
                teacher_id=teacher.id,
                solution_uuid=solution.uuid,
                year=solution.year
            )

            db.session.add(distribution)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
