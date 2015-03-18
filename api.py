#!/usr/bin/python
# -*- coding: utf-8 -*-

#
from models import (User, Account, Operation, Tag, OperationTag)
from sqlalchemy.exc import (IntegrityError)
from sqlalchemy.orm.exc import (NoResultFound)


#
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


def operation_add(session, account, amount, desc, type, tags):
    operation = Operation(aid=account, amount=amount,
            desc=desc, type=type)
    session.add(operation)
    session.flush()
    if tags:
        tag_list = []
        for tag in tags.split(','):
            try:
                t = session.query(Tag).filter(Tag.name == tag).one()
            except NoResultFound:
                t = Tag(name=tag)
                session.add(t)
            tag_list.append(t)
        session.flush()
        [session.merge(OperationTag(operation.oid, x.tid)) for x in tag_list]
        session.flush()
    return operation


def operation_get(session, oid):
    operation = session.query(Operation).get(oid)
    return operation


def operation_remove(session, oid):
    operation = session.query(Operation).get(oid)
    session.delete(operation)
    session.flush()
    return True


def operation_list(session, owner, account, tags):
    query = session.query(Operation)
    if owner and account:
        query = query.filter(Operation.aid == account).order_by(Operation.date)
    #elif owner:
    #    user = user_get(session=session, login=owner)
    #    query = query.join(Account, Operation.aid == Account.aid).filter(Account.oid == user.uid)
    #if tags:
    #    for tag in tags:
    #        query = query.join(OperationTag, Operation.oid == OperationTag.oid).join(Tag, OperationTag.tid == Tag.tid).filter(Tag.name == tag)
    return query.all()
