#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
import re
import pytest

##
from money import sdk
from money.exc import UserError, AccountError


##
def test_operation_create(app):

    with app.app_context():

        #user_login = "pawel"
        #user_password = "password!123efwmef0932098r3209r3209rm039rm2"
        #user_email = "money@example.com"

        #user = sdk.user_create(user_login, user_password, user_email, 'ddd')

        #assert re.match(r'^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$', user.uuid)
        #assert user.login == user_login
        #assert user.password != user_password
        #assert len(user.password) == 128
        #assert user.email == user_email
        #assert user.active is True
        pass
