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
    uid = Column(String(36), primary_key=True)
    login = Column(String(64), unique=True)
    password = Column(String(128))
    email = Column(String(255), unique=True)
    cdate = Column(DateTime, default=func.now())
    mdate = Column(DateTime, onupdate=func.utc_timestamp())
    active = Column(Boolean, default=True)
    #accounts = relationship('Account', backref=backref('owner', uselist=False))

    def __init__(self, login, password, email):
        self.uid = uuid.uuid4()
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
        return unicode(self.uid)

    def __repr__(self):
        return '{} ({})'.format(self.login, self.uid)


class AccountType(Base):
    __tablename__ = 'account_type'
    tid = Column(String(36), primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    sort = Column(Integer(), nullable=False)
    group = Column(Integer(), nullable=False)

    def __init__(self, name, sort, group):
        self.tid = uuid.uuid4()
        self.name = name
        self.sort = sort
        self.group = group

    def __repr__(self):
        return '{} ({})'.format(self.name, self.tid)


class Account(Base):
    __tablename__ = 'account'
    aid = Column(String(36), primary_key=True)
    oid = Column(String(36), ForeignKey('user.uid', ondelete="cascade"),
            nullable=False)
    name = Column(String(64), nullable=False, unique=True)
    initial_balance = Column(Numeric(precision=10, scale=2), nullable=False)
    type = Column(String(36), ForeignKey('account_type.tid', ondelete="cascade"),
            nullable=False)
    cdate = Column(DateTime, default=func.now(), nullable=False)
    mdate = Column(DateTime, default=func.now(), onupdate=func.utc_timestamp(),
                   nullable=False)
    active = Column(Boolean, default=True)
    owner = relationship('User', backref='accounts', uselist=False)

    def __init__(self, oid, name, initial_balance, type):
        self.aid = uuid.uuid4()
        self.oid = oid
        self.name = name
        self.initial_balance = initial_balance
        self.type = type

    def __repr__(self):
        return '{} ({})'.format(self.name, self.aid)


class Tag(Base):
    __tablename__ = 'tag'
    tid = Column(String(36), primary_key=True)
    name = Column(String(64), unique=True, nullable=False)

    def __init__(self, name):
        self.tid = uuid.uuid4()
        self.name = name

    def __repr__(self):
        return '{}:{}'.format(self.tid, self.name)


class Operation(Base):
    __tablename__ = 'operation'
    oid = Column(String(36), primary_key=True)
    aid = Column(String(36), ForeignKey('account.aid', ondelete="cascade"),
                     nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    desc = Column(String(1024), default='', nullable=False)
    date = Column(Date, default=func.now(), nullable=False)
    booked = Column(Boolean, default=False, nullable=False)
    tags = relationship('Tag', secondary='operation_tag')
    external = Column(Boolean, default=True, nullable=False)
    order_by = Column(Integer(), nullable=False,
                      autoincrement=True, unique=True)
    account = relationship('Account', uselist=False,
                           backref='operations')

    def __init__(self, aid, amount, desc, date):
        self.oid = uuid.uuid4()
        self.aid = aid
        self.amount = amount
        self.desc = desc
        self.date = date

    def __repr__(self):
        return '{:0.2f} ({})'.format(float(self.amount), self.oid)

event.listen(
    Operation.__table__, 'after_create',
    DDL("""
    ALTER TABLE operation CHANGE order_by order_by INT(11) NOT NULL AUTO_INCREMENT
    """)
)


class OperationSchedule(Base):
    __tablename__ = 'operation_schedule'
    osid = Column(String(36), primary_key=True)
    aid = Column(String(36), ForeignKey('account.aid', ondelete="cascade"),
                     nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    desc = Column(String(1024), default='', nullable=False)
    start_date = Column(Date, default=func.now(), nullable=False)
    end_date = Column(Date, nullable=True)
    period = Column(String(36), ForeignKey('operation_period.opid', ondelete="cascade"),
            nullable=False)
    tags = Column(String(4096))
    external = Column(Boolean, default=True, nullable=False)

    def __init__(self, aid, amount, desc, start_date, period, tags):
        self.oid = uuid.uuid4()
        self.aid = aid
        self.amount = amount
        self.desc = desc
        self.start_date = start_date
        self.period = period
        self.tag = tag
        self.period = period

    def __repr__(self):
        return '{:0.2f} ({})'.format(float(self.amount), self.oid)


class OperationTag(Base):
    __tablename__ = 'operation_tag'
    oid = Column(String(36), ForeignKey('operation.oid'), primary_key=True)
    tid = Column(String(36), ForeignKey('tag.tid'), primary_key=True)
    operation = relationship('Operation', uselist=False)
    tag = relationship('Tag', uselist=False)

    def __init__(self, oid, tid):
        self.oid = oid
        self.tid = tid

    def __repr__(self):
        return '{}{}'.format(self.tid, self.oid)

