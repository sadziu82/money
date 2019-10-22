#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import hashlib

from datetime import datetime
from random import random, randint
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from money.core.models import (
    Currency,
    AccountType,
    Base,
    User,
    Account,
    Tag,
    Operation,
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
    tag_add,
    tag_get,
    tag_edit,
    tag_remove,
    tag_list,
    operation_add,
    operation_get,
    operation_edit,
    operation_remove,
    operation_list,
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
    def accounts(self, users):
        currency = iter(Currency)
        accounts = []
        for user in users:
            for bank in ['PKO BP', 'Eurobank', 'mBank']:
                for at in AccountType:
                    for c in Currency:
                        accounts.append(account_add(self.session, user.id, at,
                                    '{} - {} ({})'.format(bank, at.value, c.value),
                                    0, 0, c))
        return accounts

    @pytest.fixture(scope='class')
    def tags(self, users):
        tags = []
        for user in users:
            for name in ['food', 'clothes', 'car', 'kids']:
                tags.append(tag_add(self.session, user.id, name))
        return tags


    @pytest.fixture(scope='class')
    def operations(self, accounts):
        operations = []
        for account in accounts:
            for name in ['food', 'clothes', 'car', 'kids']:
                operations.append(operation_add(self.session, account.id,
                            randint(100, 200) / 100, datetime.today(), name, False))
        return operations


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
        account = Account('123-45-6789', AccountType.CURRENT, 'JP Morgan', 0, 1000,
                Currency.PLN)
        assert len(account.id) == 36
        assert account.user_id == '123-45-6789'
        assert account.account_type == AccountType.CURRENT
        assert account.initial_balance == 0
        assert account.debit_limit == 1000

    def test_account_add(self, users):
        account = account_add(self.session, users[0].id, AccountType.CURRENT,
                              'Test Account of My Bank', 0, -1000, Currency.PLN)
        sql_account = self.session.query(Account).filter(Account.id==account.id).one()
        assert account == sql_account

    def test_account_get(self, accounts):
        sql_account = account_get(self.session, accounts[1].id)
        assert accounts[1] == sql_account
        assert accounts[1].user_id == sql_account.user_id
        assert accounts[1].account_type == sql_account.account_type
        assert accounts[1].name == sql_account.name
        assert accounts[1].initial_balance == sql_account.initial_balance
        assert accounts[1].debit_limit == sql_account.debit_limit
        assert accounts[1].currency == sql_account.currency
        assert sql_account.__repr__() == '{} ({})'.format(accounts[1].name, accounts[1].id)

    def test_account_remove(self, accounts):
        removed_id = accounts[-1].id
        account_remove(self.session, removed_id)
        with pytest.raises(NoResultFound):
            account_get(self.session, removed_id)

    def test_account_list(self, accounts):
        api_account_list = account_list(self.session)
        assert set(api_account_list) == set(accounts)


    def test_account_list_by_user(self, users, accounts):
        user_account_list = account_list(self.session, user_id=users[1].id)
        assert set(user_account_list) == set(users[1].accounts)


    def test_tag_add(self, users):
        tag = tag_add(self.session, users[0].id, 'tag_one')
        sql_tag = self.session.query(Tag).filter(Tag.id==tag.id).one()
        assert tag == sql_tag

    def test_tag_get(self, tags):
        sql_tag = tag_get(self.session, tags[1].id)
        assert tags[1] == sql_tag
        assert tags[1].user_id == sql_tag.user_id
        assert tags[1].name == sql_tag.name
        assert sql_tag.__repr__() == '{} ({})'.format(tags[1].name, tags[1].id)

    def test_tag_remove(self, tags):
        removed_id = tags[-1].id
        tag_remove(self.session, removed_id)
        with pytest.raises(NoResultFound):
            tag_get(self.session, removed_id)

    def test_tag_list(self, tags):
        api_tag_list = tag_list(self.session)
        assert set(api_tag_list) == set(tags)


    def test_tag_list_by_user(self, users, tags):
        user_tag_list = tag_list(self.session, user_id=users[1].id)
        assert set(user_tag_list) == set(users[1].tags)


    def test_operation_add(self, users, accounts):
        operation = operation_add(self.session, accounts[0].id, 23.45, datetime.today(),
                'something', False, 250, tags=['food', 'weekly'])
        sql_operation = self.session.query(Operation).filter(Operation.id==operation.id).one()
        assert operation == sql_operation

    def test_operation_get(self, operations):
        sql_operation = self.session.query(Operation).filter(Operation.id==operations[1].id).one()
        assert operations[1] == sql_operation
        assert operations[1].account_id == sql_operation.account_id
        assert operations[1].description == sql_operation.description
        assert sql_operation.__repr__() == '{:0.2f} ({})'.format(operations[1].amount, operations[1].id)

    def test_operation_edit(self, operations):
        NEW_DESC = 'some fancy description'
        NEW_AMOUNT = 1234567.89
        operation = operation_get(self.session, operations[1].id)
        operation_edit(self.session, operation.id, description = NEW_DESC, amount = NEW_AMOUNT);
        sql_operation = self.session.query(Operation).filter(Operation.id==operation.id).one()
        assert sql_operation.amount == NEW_AMOUNT
        assert sql_operation.description == NEW_DESC


    def test_operation_remove(self, operations):
        removed_id = operations[-1].id
        operation_remove(self.session, removed_id)
        with pytest.raises(NoResultFound):
            operation_get(self.session, removed_id)

    def test_operation_remove_nonexistent(self, operations):
        removed_id = '1234-56-7890'
        with pytest.raises(NoResultFound):
            operation_remove(self.session, removed_id)

    def test_operation_list_by_user(self, users, accounts, operations):
        user_accounts = [a for a in users[1].accounts]
        user_account_ids = [a.id for a in user_accounts]
        user_operations = [o for a in user_accounts for o in a.operations]
        api_operation_list = operation_list(self.session, user_ids=[users[1].id])
        assert set(api_operation_list) == set(user_operations)

    def test_operation_list_by_accounts(self, users, accounts, operations):
        user_accounts = [a for a in users[1].accounts]
        user_account_ids = [a.id for a in user_accounts]
        user_operations = [o for a in user_accounts for o in a.operations]
        api_operation_list = operation_list(self.session, account_ids=user_account_ids)
        assert set(api_operation_list) == set(user_operations)
