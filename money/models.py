#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
import uuid
import hashlib
from sqlalchemy import (Column, ForeignKey, String, Date, DateTime,
                        Numeric, Boolean, Integer, Table, func)
from sqlalchemy.orm import relationship, backref, mapped_column

##
from money.database import Base
from money.exc import UserNotValid


##
class User(Base):
    __tablename__ = 'user'
    uuid = Column(String(36), primary_key=True)
    login = Column(String(64), unique=True)
    password = Column(String(128))
    email = Column(String(255), unique=True)
    active = Column(Boolean, default=True)
    create_date = Column(DateTime, default=func.now())

    def __init__(self, login, password, email):
        self.uuid = str(uuid.uuid4())
        self.login = login
        self.password = hashlib.sha512(password.encode()).hexdigest()
        self.email = email

    def verify_password(self, password):
        try:
            assert self.password == hashlib.sha512(password.encode()).hexdigest()
        except AssertionError:
            raise UserNotValid(f'verify_password({self.login}, {password}) failed')
 
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return str(self.uuid)

    def __repr__(self):
        return '{} ({})'.format(self.login, self.uuid)


##
class Currency(Base):
    __tablename__ = 'currency'
    uuid = Column(String(36), primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    code = Column(String(8), nullable=False, unique=True)
    symbol = Column(String(4), nullable=False, unique=True)

    def __init__(self, name, code, symbol):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.code = code
        self.symbol = symbol

    def __repr__(self):
        return '{} ({})'.format(self.name, self.uuid)


##
class AccountType(Base):
    __tablename__ = 'account_type'
    uuid = Column(String(36), primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    group = Column(Integer(), nullable=False)

    def __init__(self, name, group):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.group = group

    def __repr__(self):
        return '{} ({})'.format(self.name, self.uuid)


##
class Account(Base):
    __tablename__ = 'account'
    uuid = mapped_column(String(36), primary_key=True)
    name = mapped_column(String(64), nullable=False, unique=False)
    currency_uuid = mapped_column(String(36), ForeignKey('currency.uuid',
                ondelete="cascade"), nullable=False)
    account_type_uuid = mapped_column(String(36), ForeignKey('account_type.uuid',
                ondelete="cascade"), nullable=False)
    initial_balance = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    debit_limit = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    active = mapped_column(Boolean, default=True)
    ##
    currency = relationship('Currency', backref='accounts', uselist=False)
    account_type = relationship('AccountType', backref='accounts', uselist=False)

    def __init__(self, name, currency_uuid, account_type_uuid, initial_balance, debit_limit):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.currency_uuid = currency_uuid
        self.account_type_uuid = account_type_uuid
        self.initial_balance = initial_balance
        self.debit_limit = debit_limit

    def __repr__(self):
        return '{} ({})'.format(self.name, self.uuid)


##
class UserAccount(Base):
    __tablename__ = 'user_account'
    user_uuid = Column(String(36), ForeignKey('user.uuid'), primary_key=True)
    account_uuid = Column(String(36), ForeignKey('account.uuid'), primary_key=True)
    user = relationship('User', backref='user_accounts', uselist=False)
    account = relationship('Account', backref='user_accounts', uselist=False)

    def __init__(self, user_uuid, account_uuid):
        self.user_uuid = user_uuid
        self.account_uuid = account_uuid

    def __repr__(self):
        return '{}{}'.format(self.user, self.account)


##
class Operation(Base):
    __tablename__ = 'operation'
    uuid = mapped_column(String(36), primary_key=True)
    amount = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    description = mapped_column(String(1024), default='', nullable=False)
    date = mapped_column(Date, default=func.now(), nullable=False)
    booked = mapped_column(Boolean, default=False, nullable=False)
    order = mapped_column(Integer(), nullable=False, default=500)
    ##
    sibling_operation_uuid = mapped_column(String(36), ForeignKey('operation.uuid', ondelete="cascade"), nullable=True)
    sibling_operation = relationship('Operation', uselist=False, remote_side=[uuid])
    ##
    account_uuid = mapped_column(String(36), ForeignKey('account.uuid', ondelete="cascade"), nullable=False)
    account = relationship('Account', uselist=False, backref='operations')

    def __init__(self, account_uuid, amount, description, date, booked=False, order_by=500):
        self.uuid = str(uuid.uuid4())
        self.account_uuid = account_uuid
        self.amount = amount
        self.description = description
        self.date = date
        self.booked = booked
        self.order_by = order_by

    def __repr__(self):
        return '{:0.2f} ({})'.format(float(self.amount), self.uuid)
