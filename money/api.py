#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
import random
import sqlalchemy.exc

##
from datetime import datetime
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.sql import func

##
#from money.database import db.session
from money.database import db
from money.models import User, Currency, AccountType, Account, UserAccount, Operation
from money.exc import UserError, CurrencyError, AccountError, OperationError


##
def user_create(login, password, email):
    ##
    try:
        user = User(login=login, password=password, email=email)
        db.session.add(user)
        db.session.flush()
        return user
    ##
    except:
        db.session.rollback()
        raise UserError(f'user_create({login}, {password}, {email} error')


##
def user_fetch(uuid=None, login=None):
    ## FIXME add assertion if both options are specified
    assert uuid is not None or login is not None, f'user_fetch({uuid}, {login}) must be called with uuid or login'
    ##
    try:
        if uuid is not None:
            user = db.session.query(User).where(User.uuid==uuid).one()
        elif login is not None:
            user = db.session.query(User).where(User.login==login).one()
        else:
            assert False, f'user_fetch({uuid}, {login}) call failure #1'
        return user

    except sqlalchemy.exc.NoResultFound:
        raise UserError(f"user with uuid/login '{uuid}/{login}' not found")


##
def user_validate(login, password):
    ##
    assert login is not None and password is not None, f'user_validate({login}, {password}) must be called with login and password'

    ##
    user = user_fetch(login=login)
    user.verify_password(password)

    ## all good, user and password valid
    return user


##
def currency_list():
    currency_list = db.session.query(Currency).all()
    return currency_list


##
def currency_create(name, code, symbol):
    try:
        currency = Currency(name=name, code=code, symbol=symbol)
        db.session.add(currency)
        db.session.flush()
        return currency
    except:
        db.session.rollback()
        raise CurrencyError(f'currency_create({name}, {code}, {symbol} error')


##
def account_type_list():
    account_type_list = db.session.query(AccountType).all()
    return account_type_list


##
def account_type_create(name, group):
    try:
        account_type = AccountType(name=name, group=group)
        db.session.add(account_type)
        db.session.flush()
        return account_type
    except:
        db.session.rollback()
        raise AccountTypeError(f'account_type_create({name}, {group} error')

##
def account_get_balance(uuid=None, date=None):
    ##
    return random(1000) - 400

##
def account_list(user_uuid=None):
    ##
    query = db.session.query(Account)

    ##
    if user_uuid is not None:
        subquery = db.session.query(UserAccount.account_uuid).where(UserAccount.user_uuid==user_uuid).scalar_subquery()
        query = query.filter(Account.uuid.in_(subquery))

    ##
    return query.all()


##
def account_create(name, currency, account_type, initial_balance, debit_limit, user_uuids=None):
    ## FIXME add more verification
    assert user_uuids is not None, f"must provide user parameter during account creation"
    assert len(user_uuids) > 0, f"must provide at least one user"
    ##
    try:
        ##
        account = Account(name=name, currency_uuid=currency, account_type_uuid=account_type,
                          initial_balance=initial_balance, debit_limit=debit_limit)
        db.session.add(account)
        ##
        for user_uuid in user_uuids:
            user = user_fetch(uuid=user_uuid)
            user_account = UserAccount(user_uuid=user.uuid, account_uuid=account.uuid)
            db.session.add(user_account)
        ##
        db.session.flush()
        return account
    
    except:
        db.session.rollback()
        raise AccountError(f'account_create({name}, ...) error')


##
def account_list_groupped_with_balance(user_uuid):
    ##
    result = defaultdict(lambda: defaultdict(list))

    ##
    account_types = db.session.query(AccountType).all()
    #for account_type in account_types:
    #    result[int(account_type.group / 1000)]['account_types'].append(account_type)

    ##
    subquery = db.session.query(UserAccount.account_uuid).where(UserAccount.user_uuid==user_uuid).scalar_subquery()
    accounts = db.session.query(Account).filter(Account.uuid.in_(subquery)).order_by(Account.name).all()

    for account in accounts:
        if account.account_type.name not in result[int(account.account_type.group / 1000)]['account_types']:
            result[int(account.account_type.group / 1000)]['account_types'].append(account.account_type.name)
        result[int(account.account_type.group / 1000)]['accounts'].append(account)

    groups = list(result.keys())
    for group in groups:
        if len(result[group]['accounts']) == 0:
            del result[group]

    ##
    return result


##
def account_update(uuid, name=None, currency_uuid=None, account_type_uuid=None, initial_balance=None, debit_limit=None):
    ##
    account = account_fetch(uuid=uuid)

    ##
    if name is not None:
        account.name = name
    if currency_uuid is not None:
        account.currency_uuid = currency_uuid
    if account_type_uuid is not None:
        account.account_type_uuid = account_type_uuid
    if initial_balance is not None:
        account.initial_balance = initial_balance
    if debit_limit is not None:
        account.debit_limit = debit_limit

    db.session.add(account)
    db.session.commit()


##
def account_fetch(uuid=None, user_uuid=None):
    ## FIXME add assertion if both options are specified
    assert uuid is not None, f'account_fetch({uuid}) must be called with uuid'

    ##
    try:
        query = db.session.query(Account)
        if uuid is not None:
            query = query.where(Account.uuid==uuid)
        if user_uuid is not None:
            query = query.join(UserAccount)

        ## all good, account has been found
        return query.one()

    ##
    except sqlalchemy.exc.NoResultFound:
        raise AccountNotValid(f"account uuid '{uuid}' with user_uuid '{user_uuid}' not found")


##
def account_delete(uuid=None, user_uuid=None):
    ## FIXME add assertion if both options are specified
    assert uuid is not None, f'account_fetch({uuid}) must be called with uuid'

    ##
    try:
        query = db.session.query(Account)
        if uuid is not None:
            query = query.where(Account.uuid==uuid)
        if user_uuid is not None:
            query = query.join(UserAccount)

        ## all good, account has been found
        query.delete()
        db.session.commit()
        return True

    ##
    except sqlalchemy.exc.NoResultFound:
        raise AccountNotValid(f"account uuid '{uuid}' with user_uuid '{user_uuid}' not found")


##
def user_account_list(user_uuid=None, account_uuid=None):
    ##
    query = db.session.query(UserAccount)

    ##
    if user_uuid is not None:
        query = query.filter(UserAccount.user_uuid==user_uuid)
    if account_uuid is not None:
        query = query.filter(UserAccount.account_uuid==account_uuid)

    ##
    return query.all()


##
def operation_list(account_uuids=None):
    ##
    query = db.session.query(Operation).join(Account).order_by(Operation.date, Account.name)

    ###
    #if user_uuid is not None:
    #    subquery = db.session.query(UserAccount.account_uuid).where(UserAccount.user_uuid==user_uuid).scalar_subquery()
    #    query = query.filter(Account.uuid.in_(subquery))

    ##
    return query.all()


def operation_list_with_balance(account_uuids=None, user_uuid=None):
    ##
    balance_fn = func. \
                 sum(Operation.amount). \
                 over(partition_by=Operation.account_uuid,
                      order_by=(Operation.date, Operation.booked, Account.name,
                                Operation.order, Operation.uuid), range_=(None, 0)). \
                 label('balance')
    ##
    stmt = select(Operation, Account, balance_fn). \
           join(Operation.account). \
           order_by(Operation.date, Operation.booked, Account.name)
    ##
    return db.session.execute(stmt).all()


##
def operation_fetch(uuid, user_uuid):
    ##
    try:
        query = db.session.query(Operation).where(Operation.uuid==uuid)

        ## all good, operation has been found
        return query.one()

    ##
    except sqlalchemy.exc.NoResultFound:
        raise OperationError(f"operation uuid '{uuid}' with user_uuid '{user_uuid}' not found")


##
def operation_create(account_uuid, amount, date, tags, description, user_uuid,
                     sibling_account_uuid=None, sibling_amount=None):
    ##
    try:
        operation = Operation(account_uuid=account_uuid, amount=amount, date=date,
                              description=description)
        db.session.add(operation)

        if sibling_account_uuid is not None:
            sibling_operation = Operation(account_uuid=sibling_account_uuid, amount=sibling_amount,
                                          date=date, description=description)

            db.session.add(sibling_operation)
            db.session.flush()

            if operation.account.currency.code == sibling_operation.account.currency.code:
                sibling_operation.amount = -operation.amount

            db.session.add(sibling_operation)

            operation.sibling_operation_uuid = sibling_operation.uuid
            sibling_operation.sibling_operation_uuid = operation.uuid

            db.session.add(sibling_operation)
            
        db.session.flush()

        ## all good, operation has been found
        return operation

    ##
    except sqlalchemy.exc.NoResultFound:
        raise OperationError(f"operation uuid '{uuid}' with user_uuid '{user_uuid}' not found")


##
def operation_update(uuid, account_uuid, amount, date, tags, description, user_uuid,
                     sibling_account_uuid=None, sibling_amount=None):
    ##
    try:
        operation = operation_fetch(uuid=uuid, user_uuid=user_uuid)

        operation.account_uuid = account_uuid
        operation.amount = amount
        operation.date = date
        operation.description = description
    
        db.session.add(operation)
        db.session.flush()

        if sibling_account_uuid is None and operation.sibling_operation is not None:
            sibling_operation = operation_fetch(uuid=operation.sibling_operation_uuid, user_uuid=user_uuid)
            operation.sibling_operation_uuid = None

            db.session.delete(sibling_operation)
            db.session.flush()

        elif sibling_account_uuid is not None:
            if operation.sibling_operation is None:
                sibling_operation = Operation(account_uuid=sibling_account_uuid, amount=sibling_amount,
                                              date=date, description=description)

                db.session.add(sibling_operation)
                db.session.flush()

            else:
                sibling_operation = operation_fetch(uuid=operation.sibling_operation_uuid, user_uuid=user_uuid)

            if sibling_operation.account.uuid != sibling_account_uuid:
                sibling_operation.account_uuid = sibling_account_uuid
                db.session.add(sibling_operation)

            db.session.flush()
            db.session.refresh(sibling_operation)

            if operation.account.currency.code == sibling_operation.account.currency.code:
                print('fixing amount')
                sibling_operation.amount = -operation.amount
            else:
                sibling_operation.amount = sibling_amount

            sibling_operation.date = date

            db.session.add(sibling_operation)

            operation.sibling_operation_uuid = sibling_operation.uuid
            sibling_operation.sibling_operation_uuid = operation.uuid

            db.session.add(sibling_operation)

        db.session.commit()

        ## all good, operation has been found
        return operation

    ##
    except sqlalchemy.exc.NoResultFound:
        raise OperationError(f"operation uuid '{uuid}' with user_uuid '{user_uuid}' not found")


##
def operation_delete(uuid, user_uuid):
    ##
    try:
        operation = operation_fetch(uuid=uuid, user_uuid=user_uuid)
        
        if operation.sibling_operation_uuid is not None:
            sibling_operation = operation_fetch(uuid=operation.sibling_operation_uuid, user_uuid=user_uuid)

            operation.sibling_operation_uuid = None
            sibling_operation.sibling_operation_uuid = None
            db.session.flush()
            db.session.delete(sibling_operation)

        db.session.delete(operation)
        db.session.commit()

        ## all good, operation has been found
        return True

    ##
    except sqlalchemy.exc.NoResultFound:
        raise OperationError(f"operation uuid '{uuid}' with user_uuid '{user_uuid}' not found")


##
def operation_toggle(uuid, user_uuid):
    ##
    try:
        operation = operation_fetch(uuid=uuid, user_uuid=user_uuid)
        operation.booked = not operation.booked

        db.session.add(operation)
        db.session.commit()

        ## all good, operation has been found
        return operation

    ##
    except sqlalchemy.exc.NoResultFound:
        raise OperationError(f"operation uuid '{uuid}' with user_uuid '{user_uuid}' not found")
