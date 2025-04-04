#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
import re
import pytest

##
from money import sdk
from money.exc import UserError, AccountError


##
def test_user_create(app, currencies):

    with app.app_context():

        user_login = "pawel"
        user_password = "password!123efwmef0932098r3209r3209rm039rm2"
        user_email = "money@example.com"
        base_currency_uuid = currencies[0].uuid

        user = sdk.user_create(user_login, user_password, user_email, base_currency_uuid=currencies[0].uuid)

        assert re.match(r'^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$', user.uuid)
        assert user.login == user_login
        assert user.password != user_password
        assert len(user.password) == 128
        assert user.email == user_email
        assert user.base_currency_uuid == base_currency_uuid
        assert user.active is True


##
def test_user_create_duplicated_login(app, currencies):

    with app.app_context():

        user_login = "pawel"
        user_password = "password!123efwmef0932098r3209r3209rm039rm2"
        user_email = "money@example.com"
        base_currency_uuid = currencies[0].uuid

        user_1 = sdk.user_create(user_login, user_password, user_email, base_currency_uuid=currencies[0].uuid)
        with pytest.raises(UserError):
            sdk.user_create(user_login, user_password, user_email, base_currency_uuid=currencies[0].uuid)


##
def test_user_fetch_by_uuid(app, users):

    with app.app_context():

        user_0 = sdk.user_fetch(uuid=users[0].uuid)

        assert user_0.uuid == users[0].uuid
        assert user_0.login == users[0].login
        assert user_0.password == users[0].password
        assert user_0.email == users[0].email
        assert user_0.active == users[0].active
        assert user_0.create_date == users[0].create_date

        user_1 = sdk.user_fetch(uuid=users[1].uuid)

        assert user_1.uuid == users[1].uuid
        assert user_1.login == users[1].login
        assert user_1.password == users[1].password
        assert user_1.email == users[1].email
        assert user_1.active == users[1].active
        assert user_1.create_date == users[1].create_date

        assert user_0.uuid != user_1.uuid
        assert user_0.login != user_1.login


##
def test_user_fetch_by_login(app, users):

    with app.app_context():

        user_0 = sdk.user_fetch(login=users[0].login)

        assert user_0.uuid == users[0].uuid
        assert user_0.login == users[0].login
        assert user_0.password == users[0].password
        assert user_0.email == users[0].email
        assert user_0.active == users[0].active
        assert user_0.create_date == users[0].create_date

        user_1 = sdk.user_fetch(login=users[1].login)

        assert user_1.uuid == users[1].uuid
        assert user_1.login == users[1].login
        assert user_1.password == users[1].password
        assert user_1.email == users[1].email
        assert user_1.active == users[1].active
        assert user_1.create_date == users[1].create_date

        assert user_0.uuid != user_1.uuid
        assert user_0.login != user_1.login


##
def test_user_fetch_wrong_login(app, users):

    with app.app_context():

        with pytest.raises(UserError):
            sdk.user_fetch(login='unknown')

        with pytest.raises(AssertionError):
            sdk.user_fetch()


##
def test_user_fetch_wrong_uuid(app, users):

    with app.app_context():

        with pytest.raises(UserError):
            sdk.user_fetch(uuid='unknown')


##
def test_user_fetch_no_login_uuid(app, users):

    with app.app_context():

        with pytest.raises(AssertionError):
            sdk.user_fetch()


##
def test_user_fetch_by_uuid_and_login(app, users):

    with app.app_context():

        with pytest.raises(AssertionError):
            sdk.user_fetch(uuid=users[0].uuid, login=users[0].login)
