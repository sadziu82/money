#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
import re
import pytest

##
from money import api
from money.exc import UserError, AccountError


##
def test_account_create(app, currencies, account_types, users):

    with app.app_context():

        account_name = 'PKO BP'
        account_currency = currencies[0]
        account_type = account_types[0]
        initial_balance = 123
        debit_limit = 234
        user_uuids = [users[0].uuid]

        account = api.account_create(
            name=account_name,
            currency=account_currency.uuid,
            account_type=account_type.uuid,
            initial_balance=initial_balance,
            debit_limit=debit_limit,
            user_uuids=user_uuids,
        )

        account_1 = api.account_fetch(uuid=account.uuid, user_uuid=users[0].uuid)

        assert account_1.name == account_name
        assert account_1.initial_balance == initial_balance
        assert account_1.debit_limit == debit_limit
