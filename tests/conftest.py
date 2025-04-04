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
        #'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
    })

    with app.app_context():
        init_db(app, testing=True)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


##
@pytest.fixture
def currencies(app):
    from money import sdk

    with app.app_context():
        currency_1 = sdk.currency_create("Polski Złoty", "PLN", "zł")
        currency_2 = sdk.currency_create("Euro", "EUR", "€")
        currency_3 = sdk.currency_create("US Dollar", "USD", "$")
        currency_4 = sdk.currency_create("Pound Sterling", "GBP", "£")

        sdk.db.session.commit()

        yield currency_1, currency_2, currency_3, currency_4


##
@pytest.fixture
def account_types(app):
    from money import sdk

    with app.app_context():
        account_type_1 = sdk.account_type_create("current", 1300)
        account_type_2 = sdk.account_type_create("debit", 1500)
        account_type_3 = sdk.account_type_create("credit card", 1700)
        account_type_4 = sdk.account_type_create("installment", 2300)
        account_type_5 = sdk.account_type_create("loan", 2500)
        account_type_6 = sdk.account_type_create("mortgage", 2700)
        account_type_7 = sdk.account_type_create("savings", 3300)
        account_type_7 = sdk.account_type_create("shares", 3400)
        account_type_8 = sdk.account_type_create("securities", 3500)
        account_type_9 = sdk.account_type_create("pension plan", 3600)
        account_type_10 = sdk.account_type_create("cash", 4300)
        account_type_11 = sdk.account_type_create("money to burn", 4500)
        account_type_12 = sdk.account_type_create("rainy day", 4700)

        sdk.db.session.commit()

        yield account_type_1, account_type_2, account_type_3, account_type_4, account_type_5, account_type_6, account_type_7, account_type_8, account_type_9, account_type_10, account_type_11, account_type_12


##
@pytest.fixture
def users(app, currencies):
    from money import sdk

    with app.app_context():
        user_1 = sdk.user_create(login='user1', password='password!123', email='user1@example.com',
                                 base_currency_uuid=currencies[0].uuid)
        user_2 = sdk.user_create(login='user2', password='password!456', email='user2@example.com',
                                 base_currency_uuid=currencies[1].uuid)

        sdk.db.session.commit()

        yield user_1, user_2
