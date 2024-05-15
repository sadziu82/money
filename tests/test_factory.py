#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
from money import create_app


##
def test_app_config():
    db_uri_key = 'SQLALCHEMY_DATABASE_URI'
    db_uri_value = 'sqlite:///test.db'
    db_uri_config = { db_uri_key: db_uri_value}

    ## testing config
    app_1 = create_app({'TESTING': True, db_uri_key: 'sqlite:///'})
    assert app_1.testing

    ## specified config
    app_2 = create_app(db_uri_config)
    assert not app_2.testing
    assert app_2.config[db_uri_key] == db_uri_value

    ## config taken from config.py
    app_3 = create_app()
    assert not app_3.testing
    assert app_3.config[db_uri_key]
