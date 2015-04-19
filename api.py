#!/usr/bin/python
# -*- coding: utf-8 -*-

#
from models import (User, AccountType, Account, Operation, Tag, OperationTag)
from sqlalchemy.exc import (IntegrityError)
from sqlalchemy.orm.exc import (NoResultFound)
from sqlalchemy.sql import func
from sqlalchemy import case
import datetime


#
def object_to_dict(Object):
    dictionary = Object.__dict__.copy()
    #del(dictionary['_sa_instance_state'])
    return dictionary


def user_add(session, login, password, email):
    user = User(login=login, password=password, email=email)
    session.add(user)
    session.flush()
    return user


def user_get(session, uid):
    user = session.query(User).get(uid)
    return user


def user_get_by_login(session, login):
    user = session.query(User).filter(User.login == login).one()
    return user


def user_remove(session, login):
    user = session.query(User).filter(User.login == login).one()
    session.delete(user)
    session.flush()
    return True


def user_list(session):
    return session.query(User).all()


def account_type_list(session):
    return session.query(AccountType).order_by(AccountType.group, AccountType.sort).all()


def account_add(session, owner, name, initial_balance, type):
    user = user_get(session=session, uid=owner)
    account = Account(oid=user.uid, name=name,
                      initial_balance=initial_balance, type=type)
    session.add(account)
    session.flush()
    return account


def account_get(session, aid):
    account = session.query(Account).get(aid)
    return account


def account_remove(session, aid):
    account = session.query(Account).get(aid)
    session.delete(account)
    session.flush()
    return True


def account_list(session, owner):
    if owner:
        return session.query(Account). \
            filter(Account.oid == owner).order_by(Account.name).all()
    else:
        return session.query(Account).all()


def account_list_with_balance(session, owner, to_date=None):
    if not to_date:
        to_date = datetime.datetime.today()
    return session.query(Account.aid.label('aid'),
            Account.type.label('type'),
            Account.name.label('name'),
            AccountType.name.label('type_name'),
            AccountType.sort.label('type_sort'),
            Account.initial_balance.label('initial_balance'),
            func.sum(case([(Operation.amount == None, 0)], else_=Operation.amount)).label('total_balance'),
            func.sum(case([(Operation.date <= to_date, Operation.amount)], else_=0)).label('to_date_balance')). \
        filter(Account.oid == owner). \
        join(AccountType). \
        outerjoin(Operation, Account.aid == Operation.aid). \
        group_by(Account.aid). \
        order_by(Account.name).all()


def set_operation_tags(session, oid, tags):
    tag_list = []
    session.query(OperationTag).filter(OperationTag.oid == oid).delete()
    session.flush()
    if tags:
        for tag in tags:
            try:
                t = session.query(Tag).filter(Tag.name == tag).one()
            except NoResultFound:
                t = Tag(name=tag)
                session.add(t)
            tag_list.append(t)
        session.flush()
        [session.merge(OperationTag(oid, x.tid)) for x in tag_list]
        session.flush()
    return tag_list


def operation_add(session, account, amount, desc, date, tags):
    operation = Operation(aid=account, amount=amount,
            desc=desc, date=date)
    session.add(operation)
    session.flush()
    set_operation_tags(session=session, oid=operation.oid, tags=tags)


def operation_get(session, oid):
    operation = session.query(Operation).filter(Operation.oid == oid).one()
    return operation


def operation_remove(session, oid):
    operation = session.query(Operation).get(oid)
    session.delete(operation)
    session.flush()
    return True


def operation_list(session, owner, account, tags, start_date=None, end_date=None):
    query = session.query(Operation)
    if owner and account:
        query = query.filter(Operation.aid == account). \
                filter(Operation.date >= start_date). \
                filter(Operation.date <= end_date). \
                order_by(Operation.date, Operation.order_by)
    #elif owner:
    #    user = user_get(session=session, login=owner)
    #    query = query.join(Account, Operation.aid == Account.aid).filter(Account.oid == user.uid)
    #if tags:
    #    for tag in tags:
    #        query = query.join(OperationTag, Operation.oid == OperationTag.oid).join(Tag, OperationTag.tid == Tag.tid).filter(Tag.name == tag)
    return query.all()


def tag_list(session):
    query = session.query(Tag).order_by(Tag.name)
    return query.all()
