#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
import os
import tempfile

##
import pytest

##
from money import create_app
from money.database import init_db


##
@pytest.fixture
def client(app):
    return app.test_client()


##
@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
    })

    with app.app_context():
        init_db(app)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


##
@pytest.fixture
def user(app):
    from money import api

    with app.app_context():
        user = api.user_create('pawel', 'password!123', 'money@example.com')

        api.db.session.commit()

        yield user
