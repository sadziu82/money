#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


##
def create_app(test_config=None):
    ## create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    ## load the instance config, if it exists, or test one if testing
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)

    ##
    from money.database import db
    db.init_app(app)

    ##
    from money.auth import login_manager
    login_manager.init_app(app)

    ##
    from money import auth
    app.register_blueprint(auth.bp)

    ##
    from money import view
    app.register_blueprint(view.bp)

    ###
    #@app.before_request
    #def before_request():
    #    g.db_session = db.session

    return app
