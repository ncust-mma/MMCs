# -*- coding: utf-8 -*-

import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from MMCs import db
from MMCs.models import User, Solution, Distribution, StartConfirm

fake = Faker()


def fake_root():
    user = User(
        username='Root',
        realname='Test for Root',
        permission="Root",
        remark=fake.text(),
    )
    user.set_password('mmcs4test')
    db.session.add(user)
    db.session.commit()


def fake_admin():
    user = User(
        username='admin',
        realname='Test for Admin',
        permission="Admin",
        remark=fake.text(),
    )
    user.set_password('mmcs4test')
    db.session.add(user)
    db.session.commit()


def fake_teacher():
    user = User(
        username=fake.name(),
        realname='Test for Teacher',
        permission="Teacher",
        remark=fake.text(),
    )
    user.set_password('mmcs4test')
    db.session.add(user)
    db.session.commit()
