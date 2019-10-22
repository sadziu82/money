#!/usr/bin/python
# -*- coding: utf-8 -*-

#
from money.core.models import (
    User,
    Account,
    Tag,
    Operation,
)
#, Operation, Tag, OperationTag,
        #Transfer, ScheduleTag, SchedulePeriod, Schedule)
#        SchedulePeriod, Schedule)
from sqlalchemy.exc import (IntegrityError)
from sqlalchemy.orm.exc import (NoResultFound)
from sqlalchemy.sql import func
from sqlalchemy import case
import datetime
#import dateutil


def user_add(session, login, password, email):
    user = User(
            login=login,
            password=password,
            email=email)
    session.add(user)
    session.flush()
    return user


def user_get(session, user_id):
    user = session.query(User).filter(User.id == user_id).one()
    return user


def user_get_by_login(session, login):
    user = session.query(User).filter(User.login == login).one()
    return user


def user_remove(session, user_id):
    user = session.query(User).filter(User.id==user_id).one()
    session.delete(user)
    session.flush()
    return True


def user_list(session):
    return session.query(User).all()


def account_add(session, user_id, account_type, name,
                initial_balance, debit_limit, currency):
    account = Account(
            user_id=user_id,
            account_type=account_type,
            name=name,
            initial_balance=initial_balance,
            debit_limit=debit_limit,
            currency=currency)
    session.add(account)
    session.flush()
    return account


def account_get(session, account_id):
    account = session.query(Account).filter(Account.id == account_id).one()
    return account


def account_edit(session, login, password, email):
    account = Account(
            login=login,
            password=password,
            email=email)
    session.add(account)
    session.flush()
    return account


def account_remove(session, account_id):
    account = session.query(Account).filter(Account.id==account_id).one()
    session.delete(account)
    session.flush()
    return True


def account_list(session, user_id=None):
    q = session.query(Account)
    if user_id is not None:
        q = q.filter(Account.user_id==user_id)
    return q.all()


def tag_add(session, user_id, name):
    tag = Tag(user_id=user_id,
            name=name)
    session.add(tag)
    session.flush()
    return tag


def tag_get(session, tag_id):
    tag = session.query(Tag).filter(Tag.id == tag_id).one()
    return tag


def tag_edit(session, id, user_id=None, name=None):
    tag = tag_get(id=id)
    if user_id is not None:
        tag.user_id = user_id
    if name is not None:
        tag.name = name
    session.add(tag)
    session.flush()
    return tag


def tag_remove(session, tag_id):
    tag = session.query(Tag).filter(Tag.id==tag_id).one()
    session.delete(tag)
    session.flush()
    return True


def tag_list(session, user_id=None):
    q = session.query(Tag)
    if user_id is not None:
        q = q.filter(Tag.user_id==user_id)
    return q.all()


##### def account_list_groupped(session, user_id):
#####     account_list = session.query(Account.id.label('id'),
#####             Account.account_type_id.label('account_type_id'),
#####             Account.name.label('name'),
#####             Account.initial_balance.label('initial_balance'),
#####             Account.debit_limit.label('debit_limit'),
#####             AccountType.name.label('account_type_name'),
#####             AccountType.group.label('account_type_group'),
#####             AccountType.order.label('account_type_order'),
#####             ). \
#####         filter(Account.user_id == user_id). \
#####         join(AccountType). \
#####         order_by(AccountType.group, AccountType.order, Account.name). \
#####         all()
#####     accounts = {}
#####     for account in account_list:
#####         if account.account_type_group not in accounts.keys():
#####             accounts[account.account_type_group] = {
#####                 'accounts': [],
#####                 'account_type_name': [],
#####             }
#####         if account.account_type_name not in accounts[account.account_type_group]['account_type_name']:
#####             accounts[account.account_type_group]['account_type_name'].append(account.account_type_name)
#####         accounts[account.account_type_group]['accounts'].append(object_to_dict(account))
#####     return accounts
##### 
##### 
##### def account_list_with_balance(session, user_id, end_date=None):
#####     if end_date:
#####         end_date_func = func.sum(case([(Operation.date <= end_date, Operation.amount)], else_=0)).label('end_date_balance')
#####     else:
#####         end_date_func = func.sum(Operation.amount).label('end_date_balance')
#####     
#####     query = session.query(Account.id.label('id'),
#####             Account.account_type_id.label('account_type_id'),
#####             Account.name.label('name'),
#####             Account.initial_balance.label('initial_balance'),
#####             Account.debit_limit.label('debit_limit'),
#####             AccountType.name.label('account_type_name'),
#####             AccountType.group.label('account_type_group'),
#####             AccountType.order.label('account_type_order'),
#####             func.sum(case([(Operation.amount.is_(None), 0)], else_=Operation.amount)).label('total_balance'),
#####             end_date_func,
#####         ). \
#####         filter(Account.user_id == user_id). \
#####         join(AccountType). \
#####         outerjoin(Operation). \
#####         group_by(Account.id). \
#####         order_by(AccountType.group, AccountType.order, Account.name)
#####         
#####     ## execute query
#####     accounts = {}
#####     for account in query.all():
#####         if account.account_type_group not in accounts.keys():
#####             accounts[account.account_type_group] = {
#####                 'accounts': [],
#####                 'account_type_name': [],
#####                 'end_date_balance': 0,
#####                 'total_balance': 0,
#####             }
#####         if account.end_date_balance is None:
#####             account.end_date_balance = 0
#####         if account.account_type_name not in accounts[account.account_type_group]['account_type_name']:
#####             accounts[account.account_type_group]['account_type_name'].append(account.account_type_name)
#####         accounts[account.account_type_group]['accounts'].append(object_to_dict(account))
#####         accounts[account.account_type_group]['end_date_balance'] = accounts[account.account_type_group]['end_date_balance'] + account.end_date_balance + account.initial_balance
#####         accounts[account.account_type_group]['total_balance'] = accounts[account.account_type_group]['total_balance'] + account.total_balance + account.initial_balance
#####     return accounts
##### 
##### 
##### def accounts_balance(session, account_ids, date=None):
#####     if date:
#####         balance_func = func.sum(case([(Operation.date <= date, Operation.amount)], else_=0)).label('balance')
#####     else:
#####         balance_func = func.sum(Operation.amount).label('balance')
#####     
#####     query = session.query(
#####             Operation.account_id.label('account_id'),
#####             Account.initial_balance.label('initial_balance'),
#####             Account.name.label('name'),
#####             balance_func,
#####         ). \
#####         join(Account)
#####     if len(account_ids) > 0:
#####         query = query.filter(Operation.account_id.in_((account_ids)))
#####     query = query.group_by(Operation.account_id)
#####         
#####     #E execute query
#####     accounts = {}
#####     for item in query.all():
#####         accounts[item.account_id] = item.balance + item.initial_balance
#####     return accounts
##### 
##### 
##### #def account_list_with_balance(session, user_id, end_date=None):
##### #    if not end_date:
##### #        end_date = datetime.datetime.today()
##### #    accounts = session.query(Account.id.label('id'),
##### #            Account.account_type_id.label('account_type_id'),
##### #            Account.name.label('name'),
##### #            Account.initial_balance.label('initial_balance'),
##### #            Account.debit_limit.label('debit_limit'),
##### #            AccountType.name.label('account_type_name'),
##### #            AccountType.group.label('account_type_group'),
##### #            AccountType.order.label('account_type_order'),
##### #            func.sum(case([(Operation.amount == None, 0)], else_=Operation.amount)).label('total_balance'),
##### #            func.sum(case([(Operation.date <= end_date, Operation.amount)], else_=0)).label('end_date_balance'),
##### #            ). \
##### #        filter(Account.user_id == user_id). \
##### #        join(AccountType). \
##### #        outerjoin(Operation, Account.id == Operation.account_id). \
##### #        group_by(Account.id). \
##### #        order_by(AccountType.group, AccountType.order, Account.name)
##### #    summary = {}
##### #    for account in accounts:
##### #        if account.account_type_group not in summary.keys():
##### #            summary[account.account_type_group] = {
##### #                'accounts': [],
##### #                'account_type_name': [],
##### #                'end_date_balance': 0,
##### #                'total_balance': 0,
##### #            }
##### #        if account.account_type_name not in summary[account.account_type_group]['account_type_name']:
##### #            summary[account.account_type_group]['account_type_name'].append(account.account_type_name)
##### #        summary[account.account_type_group]['accounts'].append(object_to_dict(account))
##### #        summary[account.account_type_group]['end_date_balance'] = summary[account.account_type_group]['end_date_balance'] + account.end_date_balance + account.initial_balance
##### #        summary[account.account_type_group]['total_balance'] = summary[account.account_type_group]['total_balance'] + account.total_balance + account.initial_balance
##### #    return summary


def operation_get(session, operation_id):
    operation = session.query(Operation).filter(Operation.id == operation_id).one()
    return operation


def operation_add(session, account_id, amount, date, description,
                  booked=None, order_by=500, tags=None):
    operation = Operation(account_id=account_id, amount=amount, description=description,
                          date=date, booked=booked, order_by=order_by)
    session.add(operation)
    session.flush()
    #set_operation_tags(session=session, oid=operation.oid, tags=tags)
    return operation


def operation_edit(session, id, account_id=None, amount=None, date=None, description=None,
                   booked=None, order_by=None, tags=None):
    operation = operation_get(session, id)
    if account_id is not None:
        operation.account_id = account_id
    if amount is not None:
        operation.amount = amount
    if date is not None:
        operation.date = date
    if description is not None:
        operation.description = description
    if booked is not None:
        operation.booked = booked
    if order_by is not None:
        operation.order_by = order_by
    # TODO
    #if tags is not None:
    #    operation.tags = tags
    session.add(operation)
    session.flush()
    return operation


def operation_list(session, user_ids=None, account_ids=None, tags=None,
                   start_date=None, end_date=None, last_n_operations=None):
    query = session.query(Operation)
    ##
    if user_ids is not None and len(user_ids) > 0:
        user_account_ids = [a.id for uid in user_ids for a in user_get(session, uid).accounts]
        query = query.filter(Operation.account_id.in_((user_account_ids)))
    if account_ids is not None and len(account_ids) > 0:
        query = query.filter(Operation.account_id.in_((account_ids)))
    ##
    if start_date:
        query = query.filter(Operation.date >= start_date)
    if end_date:
        query = query.filter(Operation.date <= end_date)
    ##
    if last_n_operations:
        query = query.order_by(Operation.date.desc(), Operation.booked.desc(), Operation.order_by.desc()). \
                limit(last_n_operations)
        query = query.from_self().order_by(Operation.date, Operation.booked.desc(), Operation.order_by)
    else:
        query = query.order_by(Operation.date, Operation.booked, Operation.order_by)
    return query.all()


##### def operation_list_with_balance(session, account_ids, tags=None,
#####         start_date=None, end_date=None,
#####         last_n_operations=None):
#####     query = session.query(Operation)
#####     if tags is not None:
#####         for tag in tags:
#####             query = query.join(OperationTag).filter(OperationTag.tag_id == tag)
#####     if len(account_ids) > 0:
#####         query = query.filter(Operation.account_id.in_((account_ids)))
#####     if last_n_operations:
#####         balance = accounts_balance(session=session, account_ids=account_ids)
#####         query = query.order_by(Operation.date.desc(), Operation.booked, Operation.order_by.desc()). \
#####                 limit(last_n_operations)
#####         query = query.from_self().order_by(Operation.date,
#####                 Operation.booked.desc(), Operation.order_by)
#####     else:
#####         balance = accounts_balance(session=session, account_ids=account_ids,
#####                 date=(start_date + dateutil.relativedelta.relativedelta(days=-1)))
#####         if start_date:
#####             query = query.filter(Operation.date >= start_date)
#####         if end_date:
#####             query = query.filter(Operation.date <= end_date)
#####         query = query.order_by(Operation.date, Operation.booked.desc(),
#####                 Operation.order_by)
#####     operations = query.all()
#####     if last_n_operations:
#####         for operation in reversed(operations):
#####             operation.balance = balance[operation.account_id]
#####             balance[operation.account_id] = balance.setdefault(operation.account_id, operation.account.initial_balance) - operation.amount 
#####             operation.available_funds = operation.balance - operation.account.debit_limit
#####     else:
#####         for operation in operations:
#####             balance[operation.account_id] = balance.setdefault(operation.account_id, operation.account.initial_balance) + operation.amount 
#####             operation.balance = balance[operation.account_id]
#####             operation.available_funds = balance[operation.account_id] - operation.account.debit_limit
#####     balance_report = 0
#####     for operation in operations:
#####         balance_report = balance_report + operation.amount
#####         operation.balance_report = balance_report
#####     return operations
##### 
##### 
##### def set_operation_tags(session, operation_id, tags):
#####     tag_list = []
#####     session.query(OperationTag). \
#####         filter(OperationTag.operation_id == operation_id). \
#####         delete()
#####     session.flush()
#####     if tags:
#####         for tag in tags:
#####             try:
#####                 t = session.query(Tag).filter(Tag.name == tag).one()
#####             except NoResultFound:
#####                 t = Tag(name=tag)
#####                 session.add(t)
#####             tag_list.append(t)
#####         session.flush()
#####         [session.merge(OperationTag(operation_id, t.id)) for t in tag_list]
#####         session.flush()
#####     return tag_list
##### 
##### 
##### def set_schedule_tags(session, schedule_id, tags):
#####     tag_list = []
#####     session.query(ScheduleTag). \
#####         filter(ScheduleTag.schedule_id == schedule_id). \
#####         delete()
#####     session.flush()
#####     if tags:
#####         for tag in tags:
#####             try:
#####                 t = session.query(Tag).filter(Tag.name == tag).one()
#####             except NoResultFound:
#####                 t = Tag(name=tag)
#####                 session.add(t)
#####             tag_list.append(t)
#####         session.flush()
#####         [session.merge(ScheduleTag(schedule_id, t.id)) for t in tag_list]
#####         session.flush()
#####     return tag_list
##### 
##### 
##### def transfer_get(session, transfer_id):
#####     transfer = session.query(Transfer).get(transfer_id)
#####     return transfer
##### 
##### 
##### def transfer_add(session, operation_from_id, operation_to_id):
#####     transfer = Transfer(operation_from_id=operation_from_id,
#####             operation_to_id=operation_to_id)
#####     session.add(transfer)
#####     session.flush()
#####     return transfer
##### 
##### 
##### def transfer_remove(session, transfer_id):
#####     transfer = transfer_get(session=session, transfer_id=transfer_id)
#####     session.delete(transfer)
#####     operation_remove(session, operation_id=transfer.operation_from_id)
#####     operation_remove(session, operation_id=transfer.operation_to_id)
#####     session.flush()
#####     return True


def operation_remove(session, operation_id):
    # TODO remove tags
    #set_operation_tags(session=session, operation_id=operation_id, tags=None)
    operation = operation_get(session, operation_id)
    session.delete(operation)
    session.flush()
    return True


##### #def schedule_period_get(session, id):
##### #    schedule_period = session.query(SchedulePeriod).get(id)
##### #    return schedule_period
##### #
##### #
##### def schedule_period_list(session):
#####     query = session.query(SchedulePeriod). \
#####             order_by(SchedulePeriod.months, SchedulePeriod.days)
#####     return query.all()
##### 
##### 
##### def schedule_add(session, account_1_id, account_2_id, amount, desc,
#####         schedule_period_id, start_date, end_date):
#####     schedule = Schedule(account_1_id=account_1_id, account_2_id=account_2_id,
#####             amount=amount, desc=desc,
#####             schedule_period_id=schedule_period_id,
#####             start_date=start_date, end_date=end_date)
#####     session.add(schedule)
#####     session.flush()
#####     return schedule
##### 
##### 
##### def schedule_remove(session, schedule_id):
#####     schedule = schedule_get(session=session, schedule_id=schedule_id)
#####     session.delete(schedule)
#####     session.flush()
#####     return True
##### 
##### 
##### def schedule_get(session, schedule_id):
#####     schedule = session.query(Schedule).get(schedule_id)
#####     return schedule
##### 
##### 
##### def schedule_transfer(session, schedule_id, max_date):
#####     schedule = session.query(Schedule).get(schedule_id)
#####     ##
#####     if schedule.end_date:
#####         end_date = min(str(schedule.end_date), max_date)
#####     else:
#####         end_date = max_date
#####     ##
#####     current_date = schedule.start_date
#####     #print current_date, end_date
#####     ##
#####     while str(current_date) <= end_date:
#####         if schedule.account_2_id:
#####             operation_from = operation_add(session=session,
#####                     account_id=schedule.account_1_id,
#####                     amount=-schedule.amount,
#####                     description=schedule.desc,
#####                     date=current_date)
#####             set_operation_tags(session=session, operation_id=operation_from.id,
#####                     tags=[x.name for x in schedule.tags])
#####             operation_to = operation_add(session=session,
#####                     account_id=schedule.account_2_id,
#####                     amount=schedule.amount,
#####                     description=schedule.desc,
#####                     date=current_date)
#####             set_operation_tags(session=session, operation_id=operation_to.id,
#####                     tags=[x.name for x in schedule.tags])
#####             transfer = transfer_add(session=session,
#####                     operation_from_id=operation_from.id,
#####                     operation_to_id=operation_to.id)
#####             operation_from.transfer_id = transfer.id
#####             operation_to.transfer_id = transfer.id
#####         else:
#####             operation = operation_add(session=session,
#####                     account_id=schedule.account_1_id,
#####                     amount=schedule.amount,
#####                     description=schedule.desc,
#####                     date=current_date)
#####             set_operation_tags(session=session, operation_id=operation.id,
#####                     tags=[x.name for x in schedule.tags])
#####         current_date = current_date + dateutil.relativedelta.relativedelta(
#####                 months=schedule.schedule_period.months, days=schedule.schedule_period.days)
#####         ## break loop if schedule is 'once' only
#####         if schedule.start_date == current_date:
#####             break
#####         schedule.start_date = current_date
##### 
#####     session.flush()
##### 
##### 
##### def schedule_list(session, user_id, end_date=None):
#####     query = session.query(Schedule). \
#####         order_by(Schedule.start_date)
#####     return query.all()
##### 
##### 
##### def tag_list(session):
#####     query = session.query(Tag).order_by(Tag.name)
#####     return query.all()
##### 
##### 
##### def account_monthly_balance_per_account(session, account_ids,
#####         start_date=None, end_date=None):
#####     query = session.query(Operation)
#####     if len(account_ids) > 0:
#####         query = query.filter(Operation.account_id.in_((account_ids)))
#####     initial_balance = accounts_balance(session=session, account_ids=account_ids,
#####             date=(start_date + dateutil.relativedelta.relativedelta(days=-1)))
#####     if start_date:
#####         query = query.filter(Operation.date >= start_date)
#####     if end_date:
#####         query = query.filter(Operation.date <= end_date)
#####     query = query.order_by(Operation.date, Operation.booked.desc(),
#####             Operation.order_by)
#####     operations = query.all()
#####     ##
#####     current_balance = accounts_balance(session=session, account_ids=account_ids,
#####             date=(start_date + dateutil.relativedelta.relativedelta(days=-1)))
#####     balance = {}
#####     for operation in operations:
#####         year_month = operation.date.strftime('%Y-%m')
#####         balance.setdefault(year_month, {})
#####         balance[year_month].setdefault(operation.account_id, {
#####             'monthly_balance': 0,
#####             'total_balance': 0,
#####             'monthly_income': 0,
#####             'monthly_expenses': 0,
#####         })
#####         if operation.amount < 0:
#####             balance[year_month][operation.account_id]['monthly_expenses'] = balance[year_month][operation.account_id]['monthly_expenses'] + operation.amount 
#####         if operation.amount > 0:
#####             balance[year_month][operation.account_id]['monthly_income'] = balance[year_month][operation.account_id]['monthly_income'] + operation.amount 
#####         balance[year_month][operation.account_id]['monthly_balance'] = balance[year_month][operation.account_id]['monthly_balance'] + operation.amount 
#####         balance[year_month][operation.account_id]['total_balance'] = current_balance[operation.account_id] + operation.amount 
#####         current_balance[operation.account_id] = balance[year_month][operation.account_id]['total_balance']
#####     return balance
##### 
##### 
##### def account_monthly_balance(session, account_ids,
#####         start_date=None, end_date=None):
#####     query = session.query(Operation)
#####     if len(account_ids) > 0:
#####         query = query.filter(Operation.account_id.in_((account_ids)))
#####     initial_balance = accounts_balance(session=session, account_ids=account_ids,
#####             date=(start_date + dateutil.relativedelta.relativedelta(days=-1)))
#####     if start_date:
#####         query = query.filter(Operation.date >= start_date)
#####     if end_date:
#####         query = query.filter(Operation.date <= end_date)
#####     query = query.order_by(Operation.date, Operation.booked.desc(),
#####             Operation.order_by)
#####     operations = query.all()
#####     ##
#####     current_balance = accounts_balance(session=session, account_ids=account_ids,
#####             date=(start_date + dateutil.relativedelta.relativedelta(days=-1)))
#####     start_balance = 0
#####     for balance in current_balance:
#####         start_balance = start_balance + current_balance[balance]
#####     balance = {}
#####     for operation in operations:
#####         year_month = operation.date.strftime('%Y-%m')
#####         balance.setdefault(year_month, {
#####             'monthly_balance': 0,
#####             'total_balance': 0,
#####             'monthly_income': 0,
#####             'monthly_expenses': 0,
#####         })
#####         if operation.amount < 0:
#####             balance[year_month]['monthly_expenses'] = balance[year_month]['monthly_expenses'] + operation.amount 
#####         if operation.amount > 0:
#####             balance[year_month]['monthly_income'] = balance[year_month]['monthly_income'] + operation.amount 
#####         balance[year_month]['monthly_balance'] = balance[year_month]['monthly_balance'] + operation.amount 
#####         balance[year_month]['total_balance'] = start_balance + operation.amount 
#####         start_balance = balance[year_month]['total_balance']
#####     return balance
