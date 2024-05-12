#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
import uuid
import hashlib
from sqlalchemy import (Column, ForeignKey, String, Date, DateTime,
                        Numeric, Boolean, Integer, Table, func)
from sqlalchemy.orm import relationship, backref

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
