#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
class Config:
    ## location of database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/money.sqlite'

    ## to generate new secret use
    ## python -c 'import secrets; print(secrets.token_hex())'
    SECRET_KEY = '25f15c8339648679f4c3b440568d8422be482f6f54f38b47578a49ed05109e58'
