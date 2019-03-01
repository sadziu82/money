#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import hashlib

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from money.core.models import (
    Base,
    User,
    Account,
    AccountType
)
from money.core.api import (
    user_add,
    user_get,
    user_get_by_login,
    user_remove,
    user_list,
    account_add,
    account_get,
    account_edit,
    account_remove,
    account_list,
)

########################################################################
## following will create sqlite db in memory
engine = create_engine('sqlite://')

@event.listens_for(engine, 'connect')
def do_connect(dbapi_connection, connection_record):
    # disable pysqlite's emitting of the BEGIN statement entirely.
    # also stops it from emitting COMMIT before any DDL.
    dbapi_connection.isolation_level = None

@event.listens_for(engine, 'begin')
def do_begin(conn):
    # emit our own BEGIN
    conn.execute('BEGIN')

    
## 
class TestCoreAPI(object):
    @classmethod
    def setup_class(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine)

    @classmethod
    def teardown_class(self):
        Base.metadata.drop_all(engine)

    @classmethod
    def setup_method(self):
        self.session.begin_nested()

    @classmethod
    def teardown_method(self):
        self.session.rollback()

    @pytest.fixture(scope='class')
    def users(self):
        users = []
        users.append(user_add(self.session, 'test_1', 'pass_1',
                    'fake1@email.com'))
        users.append(user_add(self.session, 'test_2', 'pass_2',
                    'fake2@email.com'))
        users.append(user_add(self.session, 'test_3', 'pass_3',
                    'fake3@email.com'))
        return users

    @pytest.fixture(scope='class')
    def account_types(self, users):
        account_types = []
        account_types.append(account_type_add(self.session, users[0].id, 'current',
                    100, 10))
        account_types.append(account_type_add(self.session, users[0].id, 'debit',
                    100, 20))
        account_types.append(account_type_add(self.session, users[0].id, 'savings',
                    200, 50))
        account_types.append(account_type_add(self.session, users[0].id, 'loan',
                    300, None))
        account_types.append(account_type_add(self.session, users[0].id, 'installment',
                    300, None))
        return account_types

    def test_user_instance(self):
        user = User('tester', 'test_pass', 'email@example.com')
        assert len(user.id) == 36
        assert user.login == 'tester'
        assert user.password == hashlib.sha512('test_pass'.encode(
                    'utf-8')).hexdigest()
        assert user.email == 'email@example.com'

    def test_user_add(self):
        user = user_add(self.session, 'test', 'password', 'email@example.com')
        sql_user = self.session.query(User).filter(User.id==user.id).one()
        assert user == sql_user

    def test_user_get(self, users):
        sql_user = user_get(self.session, users[1].id)
        assert users[1] == sql_user
        assert users[1].id == sql_user.get_id()
        assert sql_user.is_anonymous() == False
        assert sql_user.is_active() == True
        assert sql_user.is_authenticated() == True
        assert sql_user.__repr__() == '{} ({})'.format(users[1].login, users[1].id)

    def test_user_get_by_login(self, users):
        sql_user = user_get_by_login(self.session, users[1].login)
        assert users[1] == sql_user

    def test_user_remove(self, users):
        removed_id = users[-1].id
        user_remove(self.session, removed_id)
        with pytest.raises(NoResultFound):
            user_get(self.session, removed_id)

    def test_user_list(self, users):
        api_user_list = user_list(self.session)
        assert set(api_user_list) == set(users)

    def test_account_instance(self):
        account = Account('123-45-6789', AccountType.CURRENT, 'JP Morgan', 0, 1000)
        assert len(account.id) == 36
        assert account.user_id == '123-45-6789'
        assert account.account_type == AccountType.CURRENT
        assert account.initial_balance == 0
        assert account.debit_limit == 1000

    #def test_account_add(self):
    #    account = account_add(self.session, 'test', 'password', 'email@example.com')
    #    sql_account = self.session.query(Account).filter(Account.id==account.id).one()
    #    assert account == sql_account


    #def test_account_get(self, accounts):
    #    sql_account = account_get(self.session, accounts[1].id)
    #    assert accounts[1] == sql_account
    #    assert accounts[1].id == sql_account.get_id()
    #    assert sql_account.is_anonymous() == False
    #    assert sql_account.is_active() == True
    #    assert sql_account.is_authenticated() == True
    #    assert sql_account.__repr__() == '{} ({})'.format(accounts[1].login, accounts[1].id)

    #def test_account_get_by_login(self, accounts):
    #    sql_account = account_get_by_login(self.session, accounts[1].login)
    #    assert accounts[1] == sql_account

    #def test_account_remove(self, accounts):
    #    removed_id = accounts[-1].id
    #    account_remove(self.session, removed_id)
    #    with pytest.raises(NoResultFound):
    #        account_get(self.session, removed_id)

    #def test_account_list(self, accounts):
    #    api_account_list = account_list(self.session)
    #    assert set(api_account_list) == set(accounts)
