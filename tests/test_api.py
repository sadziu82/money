#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
import re
import pytest

##
from money import api
from money.exc import UserError, AccountError


##
def test_user_create(app):

    with app.app_context():

        user_login = "pawel"
        user_password = "password!123efwmef0932098r3209r3209rm039rm2"
        user_email = "money@example.com"

        user = api.user_create(user_login, user_password, user_email)

        assert re.match(r'^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$', user.uuid)
        assert user.login == user_login
        assert user.password != user_password
        assert len(user.password) == 128
        assert user.email == user_email
        assert user.active is True

##
def test_user_fetch_by_uuid(app, user):

    with app.app_context():

        user_by_uuid = api.user_fetch(uuid=user.uuid)

        assert user_by_uuid.uuid == user.uuid
        assert user_by_uuid.login == user.login
        assert user_by_uuid.password == user.password
        assert user_by_uuid.email == user.email
        assert user_by_uuid.active == user.active
        assert user_by_uuid.create_date == user.create_date

##
def test_user_fetch_by_login(app, user):

    with app.app_context():

        user_by_login = api.user_fetch(login=user.login)

        assert user_by_login.uuid == user.uuid
        assert user_by_login.login == user.login
        assert user_by_login.password == user.password
        assert user_by_login.email == user.email
        assert user_by_login.active == user.active
        assert user_by_login.create_date == user.create_date

##
def test_user_fetch_wrong_login(app, user):

    with app.app_context():

        with pytest.raises(UserError):
            api.user_fetch(login='unknown')

        with pytest.raises(AssertionError):
            api.user_fetch()
##
def test_user_fetch_wrong_uuid(app, user):

    with app.app_context():

        with pytest.raises(UserError):
            api.user_fetch(uuid='unknown')

##
def test_user_fetch_no_login_uuid(app, user):

    with app.app_context():

        with pytest.raises(AssertionError):
            api.user_fetch()
