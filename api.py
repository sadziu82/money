#!/usr/bin/python
# -*- coding: utf-8 -*-

#
from models import (User, AccountType, Account, Operation, Tag, OperationTag)
#        SchedulePeriod, Schedule)
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
    user = User(
            login=login,
            password=password,
            email=email)
    session.add(user)
    session.flush()
    return user


def user_get(session, user_id):
    user = session.query(User).get(user_id)
    return user


def user_get_by_login(session, login):
    user = session.query(User).filter(User.login == login).one()
    return user


def user_remove(session, user_id):
    user = session.query(User).get(user_id).one()
    session.delete(user)
    session.flush()
    return True


def user_list(session):
    return session.query(User).all()


def account_type_list(session):
    return session.query(AccountType). \
        order_by(AccountType.group, AccountType.order).all()


def account_add(session, account_type_id, user_id, name, initial_balance, debit_limit):
    user = user_get(session=session, user_id=user_id)
    account = Account(
            account_type_id=account_type_id,
            user_id=user_id,
            name=name,
            initial_balance=initial_balance,
            debit_limit=debit_limit)
    session.add(account)
    session.flush()
    return account


def account_get(session, account_id):
    account = session.query(Account).get(account_id)
    return account


def account_remove(session, account_id):
    account = session.query(Account).get(account_id)
    session.delete(account)
    session.flush()
    return True


def account_list(session, user_id):
    return session.query(Account). \
        filter(Account.user_id == user_id).order_by(Account.name).all()


def account_list_with_balance(session, user_id, to_date=None):
    if not to_date:
        to_date = datetime.datetime.today()
    accounts = session.query(Account.id.label('id'),
            Account.account_type_id.label('account_type_id'),
            Account.name.label('name'),
            Account.initial_balance.label('initial_balance'),
            Account.debit_limit.label('debit_limit'),
            AccountType.name.label('account_type_name'),
            AccountType.group.label('account_type_group'),
            AccountType.order.label('account_type_order'),
            func.sum(case([(Operation.amount == None, 0)], else_=Operation.amount)).label('total_balance'),
            func.sum(case([(Operation.date <= to_date, Operation.amount)], else_=0)).label('to_date_balance'),
            ). \
        filter(Account.user_id == user_id). \
        join(AccountType). \
        outerjoin(Operation, Account.id == Operation.account_id). \
        group_by(Account.id). \
        order_by(AccountType.group, AccountType.order, Account.name)
    summary = {}
    for account in accounts:
        if account.account_type_group not in summary.keys():
            summary[account.account_type_group] = {
                'accounts': [],
                'account_type_name': [],
                'to_date_balance': 0,
                'total_balance': 0,
            }
        if account.account_type_name not in summary[account.account_type_group]['account_type_name']:
            summary[account.account_type_group]['account_type_name'].append(account.account_type_name)
        summary[account.account_type_group]['accounts'].append(object_to_dict(account))
        summary[account.account_type_group]['to_date_balance'] = summary[account.account_type_group]['to_date_balance'] + account.to_date_balance + account.initial_balance
        summary[account.account_type_group]['total_balance'] = summary[account.account_type_group]['total_balance'] + account.total_balance + account.initial_balance
    return summary


#def set_operation_tags(session, oid, tags):
#    tag_list = []
#    session.query(OperationTag).filter(OperationTag.oid == oid).delete()
#    session.flush()
#    if tags:
#        for tag in tags:
#            try:
#                t = session.query(Tag).filter(Tag.name == tag).one()
#            except NoResultFound:
#                t = Tag(name=tag)
#                session.add(t)
#            tag_list.append(t)
#        session.flush()
#        [session.merge(OperationTag(oid, x.tid)) for x in tag_list]
#        session.flush()
#    return tag_list
#
#
#def operation_add(session, account, amount, desc, date, tags):
#    operation = Operation(aid=account, amount=amount,
#            desc=desc, date=date)
#    session.add(operation)
#    session.flush()
#    set_operation_tags(session=session, oid=operation.oid, tags=tags)
#
#
#def operation_get(session, oid):
#    operation = session.query(Operation).filter(Operation.oid == oid).one()
#    return operation
#
#
#def transfer_get(session, tid):
#    operations = session.query(Operation).filter(Operation.tid == tid).all()
#    return operations
#
#
#def operation_remove(session, oid):
#    operation = session.query(Operation).get(oid)
#    session.delete(operation)
#    session.flush()
#    return True
#
#
#def operation_list(session, owner, account, tags, start_date=None, end_date=None):
#    query = session.query(Operation)
#    if owner and account:
#        query = query.filter(Operation.aid == account). \
#                filter(Operation.date >= start_date). \
#                filter(Operation.date <= end_date). \
#                order_by(Operation.date, Operation.order_by)
#    #elif owner:
#    #    user = user_get(session=session, login=owner)
#    #    query = query.join(Account, Operation.aid == Account.aid).filter(Account.oid == user.uid)
#    #if tags:
#    #    for tag in tags:
#    #        query = query.join(OperationTag, Operation.oid == OperationTag.oid).join(Tag, OperationTag.tid == Tag.tid).filter(Tag.name == tag)
#    return query.all()
#
#
#def schedule_period_get(session, id):
#    schedule_period = session.query(SchedulePeriod).get(id)
#    return schedule_period
#
#
#def schedule_period_list(session):
#    query = session.query(SchedulePeriod). \
#            order_by(SchedulePeriod.months, SchedulePeriod.days)
#    return query.all()
#
#
#def schedule_add(session, a1, a2, amount, desc, start_date, period_id, end_date,
#        tags, external):
#    schedule = Schedule(a1=a1, a2=a2, amount=amount, desc=desc,
#            start_date=start_date, period_id=period_id, end_date=end_date, tags=tags,
#            external=external)
#    session.add(schedule)
#    session.flush()
#    #set_schedule_tags(session=session, id=schedule.id, tags=tags)
#
#
#def schedule_get(session, id):
#    schedule = session.query(Schedule).get(id)
#    return schedule
#
#
#def schedule_list(session, owner, to_date=None):
#    query = session.query(Schedule). \
#            filter(Schedule.start_date <= to_date). \
#            order_by(Schedule.start_date)
#    return query.all()
#
#
#def tag_list(session):
#    query = session.query(Tag).order_by(Tag.name)
#    return query.all()
