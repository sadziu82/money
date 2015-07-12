#!/usr/bin/python
# -*- coding: utf-8 -*-

# base imports
import uuid
import hashlib

# 
from sqlalchemy import (Column, ForeignKey, String, Date, DateTime,
                        Numeric, Boolean, Integer, Table, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy import event
from sqlalchemy.schema import DDL


#
Base = declarative_base()

#
class User(Base):
    __tablename__ = 'user'
    id = Column(String(36), primary_key=True)
    login = Column(String(64), unique=True)
    password = Column(String(128))
    email = Column(String(255), unique=True)
    active = Column(Boolean, default=True)
    cdate = Column(DateTime, default=func.now())
    mdate = Column(DateTime, onupdate=func.utc_timestamp())

    def __init__(self, login, password, email):
        self.id = uuid.uuid4()
        self.login = login
        self.password = hashlib.sha512(password).hexdigest()
        self.email = email

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '{} ({})'.format(self.login, self.id)


class AccountType(Base):
    __tablename__ = 'account_type'
    id = Column(String(36), primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    group = Column(Integer(), nullable=False)
    order = Column(Integer(), nullable=False)

    def __init__(self, name, group, order):
        self.id = uuid.uuid4()
        self.name = name
        self.group = group
        self.order = order

    def __repr__(self):
        return '{} ({})'.format(self.name, self.id)


class Account(Base):
    __tablename__ = 'account'
    id = Column(String(36), primary_key=True)
    account_type_id = Column(String(36), ForeignKey('account_type.id',
                ondelete="cascade"), nullable=False)
    user_id = Column(String(36), ForeignKey('user.id', ondelete="cascade"),
            nullable=False)
    name = Column(String(64), nullable=False, unique=True)
    initial_balance = Column(Numeric(precision=10, scale=2), nullable=False)
    debit_limit = Column(Numeric(precision=10, scale=2), nullable=False)
    active = Column(Boolean, default=True)
    cdate = Column(DateTime, default=func.now(), nullable=False)
    mdate = Column(DateTime, default=func.now(), onupdate=func.utc_timestamp(),
                   nullable=False)
    ## backrefs
    user = relationship('User', backref='accounts', uselist=False)
    account_type = relationship('AccountType', backref='accounts', uselist=False)

    def __init__(self, account_type_id, user_id, name, initial_balance, debit_limit):
        self.id = uuid.uuid4()
        self.account_type_id = account_type_id
        self.user_id = user_id
        self.name = name
        self.initial_balance = initial_balance
        self.debit_limit = debit_limit

    def __repr__(self):
        return u'{} ({})'.format(self.name, self.id)


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(String(36), primary_key=True)
    name = Column(String(64), unique=True, nullable=False)

    def __init__(self, name):
        self.id = uuid.uuid4()
        self.name = name

    def __repr__(self):
        return '{} ({})'.format(self.name, self.id)


class Operation(Base):
    __tablename__ = 'operation'
    id = Column(String(36), primary_key=True)
    account_id = Column(String(36), ForeignKey('account.id', ondelete="cascade"),
                     nullable=False)
    transfer_id = Column(String(36), nullable=True)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    description = Column(String(1024), default='', nullable=False)
    date = Column(Date, default=func.now(), nullable=False)
    booked = Column(Boolean, default=False, nullable=False)
    order_by = Column(Integer(), nullable=False, default=500)
    tags = relationship('Tag', secondary='operation_tag')
    account = relationship('Account', uselist=False,
                           backref='operations')

    def __init__(self, account_id, amount, description, date, transfer_id=None, booked=False, order_by=500):
        self.id = uuid.uuid4()
        self.account_id = account_id
        self.amount = amount
        self.description = description
        self.date = date
        self.transfer_id = transfer_id
        self.booked = booked
        self.order_by = order_by

    def __repr__(self):
        return '{:0.2f} ({})'.format(float(self.amount), self.oid)

event.listen(
    Operation.__table__, 'after_create',
    DDL("""
    ALTER TABLE operation CHANGE order_by order_by INT(11) NOT NULL AUTO_INCREMENT
    """)
)


class OperationTag(Base):
    __tablename__ = 'operation_tag'
    operation_id = Column(String(36), ForeignKey('operation.id'), primary_key=True)
    tag_id = Column(String(36), ForeignKey('tag.id'), primary_key=True)
    operation = relationship('Operation', uselist=False)
    tag = relationship('Tag', uselist=False)

    def __init__(self, operation_id, tag_id):
        self.operation_id = operation_id
        self.tag_id = tag_id

    def __repr__(self):
        return '{}{}'.format(self.operation_tag, self.tag_id)


class Transfer(Base):
    __tablename__ = 'transfer'
    id = Column(String(36), primary_key=True)
    operation_from_id = Column(String(36), ForeignKey('operation.id'), nullable=False)
    operation_to_id = Column(String(36), ForeignKey('operation.id'), nullable=False)
    operation_from = relationship('Operation', foreign_keys=operation_from_id,
            uselist=False)
    operation_to = relationship('Operation', foreign_keys=operation_to_id,
            uselist=False)

    def __init__(self, operation_from_id, operation_to_id):
        self.id = uuid.uuid4()
        self.operation_from_id = operation_from_id
        self.operation_to_id = operation_to_id

    def __repr__(self):
        return '{} - {} - {}'.format(self.id,
                self.operation_from_id,
                self.operation_to_id)


class SchedulePeriod(Base):
    __tablename__ = 'schedule_period'
    id = Column(String(36), primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    days = Column(Integer(), nullable=False)
    months = Column(Integer(), nullable=False)


class ScheduleTag(Base):
    __tablename__ = 'schedule_tag'
    schedule_id = Column(String(36), ForeignKey('schedule.id'), primary_key=True)
    tag_id = Column(String(36), ForeignKey('tag.id'), primary_key=True)
    schedule = relationship('Schedule', uselist=False)
    tag = relationship('Tag', uselist=False)

    def __init__(self, schedule_id, tag_id):
        self.schedule_id = schedule_id
        self.tag_id = tag_id

    def __repr__(self):
        return '{}:{}'.format(self.schedule_tag, self.tag_id)


class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(String(36), primary_key=True)
    account_1_id = Column(String(36), ForeignKey('account.id', ondelete="cascade"),
            nullable=False)
    account_2_id = Column(String(36), ForeignKey('account.id', ondelete="cascade"),
            nullable=True)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    desc = Column(String(1024), default='', nullable=False)
    schedule_period_id = Column(String(36), ForeignKey('schedule_period.id',
                ondelete="cascade"),
            nullable=False)
    start_date = Column(Date, default=func.now(), nullable=False)
    end_date = Column(Date, nullable=True)
    tags = relationship('Tag', secondary='schedule_tag')
    account_1 = relationship('Account', uselist=False,
            primaryjoin="Schedule.account_1_id == Account.id")
    account_2 = relationship('Account', uselist=False,
            primaryjoin="Schedule.account_2_id == Account.id")
    schedule_period = relationship('SchedulePeriod', uselist=False)

    def __init__(self, account_1_id, account_2_id, amount, desc,
            schedule_period_id, start_date, end_date):
        self.id = uuid.uuid4()
        self.account_1_id = account_1_id
        self.account_2_id = account_2_id
        self.amount = amount
        self.desc = desc
        self.schedule_period_id = schedule_period_id
        self.start_date = start_date
        self.end_date = end_date
