#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
import sqlalchemy.exc

##
from money.database import db_session
from money.models import User
from money.exc import UserNotValid


##
def user_fetch(uuid=None, login=None):
    ## FIXME add assertion if both options are specified
    assert uuid is not None or login is not None, f'user_fetch({uuid}, {login}) must be called with uuid or login'

    ##
    try:
        if uuid is not None:
            user = db_session.query(User).where(User.uuid==uuid).one()
        elif login is not None:
            user = db_session.query(User).where(User.login==login).one()
        else:
            assert False, f'user_fetch({uuid}, {login}) call failure #1'

    except sqlalchemy.exc.NoResultFound:
        raise UserNotValid(f"user with login '{login}' not found")

    ## all good, user has been found
    return user

##
def user_validate(login, password):
    ##
    assert login is not None and password is not None, f'user_validate({login}, {password}) must be called with login and password'

    ##
    user = user_fetch(login=login)
    user.verify_password(password)

    ## all good, user and password valid
    return user
