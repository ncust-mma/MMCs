# -*- coding: utf-8 -*-

from faker import Faker
from sqlalchemy.sql.expression import func

from MMCs import db
from MMCs.models import (Distribution, Solution, StartConfirm, UploadFileType,
                         User)

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
        except:
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
            except:
                db.session.rollback()


def fake_file_type(count=5):
    for _ in range(count):
        upload_file_type = UploadFileType(
            file_type=fake.file_extension()
        )
        db.session.add(upload_file_type)

        try:
            db.session.commit()
        except:
            db.session.rollback()
