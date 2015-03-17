#!/usr/bin/python

##
import uuid
import hashlib
import sqlalchemy
import ConfigParser

##
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from flask import Flask, request, render_template, redirect, url_for, g, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import (LoginManager,
                             login_user, logout_user,
                             current_user, login_required
                             )
#from flask.forms import LoginForm
import logging
from logging.handlers import RotatingFileHandler


# FIXME
import sys
sys.path.append('/srv/money.ithaca.pl/')
import api
import models


#
CONFIG_FILE = '/etc/money.ithaca.pl/money.cfg'
config = ConfigParser.SafeConfigParser()
config.read(CONFIG_FILE)

# database engine
DB_ENDPOINT = config.get('prod', 'db_uri')
engine = create_engine(DB_ENDPOINT, echo=False)
Session = sessionmaker()
Session.configure(bind=engine)

#
money = Flask(__name__)
money.config['SQLALCHEMY_DATABASE_URI'] = DB_ENDPOINT
db = SQLAlchemy(money)

#
money.secret_key = '9OjJw9u0ONFsrzv2MwN40EsOSyYahk1gN6tvJPKa'
money.config['SESSION_TYPE'] = 'filesystem'
login_manager = LoginManager()
login_manager.init_app(money)
login_manager.login_view = 'login'

#
@contextmanager
def session_scope():
    session = Session()
    try:
        session.execute('set auto_increment_increment = 10')
        session.execute('set auto_increment_offset = 10')
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


#
@login_manager.user_loader
def load_user(uid):
    return api.user_get(session=db.session, uid=uid)

@money.before_request
def before_request():
    g.user = current_user
    g.session = db.session
    g.logger = money.logger


@money.route('/', methods=['GET'])
def index():
    if g.user.is_authenticated() is False:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('account_list'))


@money.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    login = request.form['login']
    password = request.form['password']
    user = api.user_get_by_login(session=g.session, login=login)
    if user is None:
        return redirect(url_for('login'))
    login_user(user)
    return redirect(request.args.get('next') or url_for('index'))


@money.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index')) 


@money.route('/my_account')
@login_required
def my_account():
    return redirect(url_for('index')) 


@money.route('/ajax/account/edit/<aid>', methods=['GET'])
@login_required
def ajax_account_edit(aid):
    account = api.account_get(session=g.session, aid=aid)
    return render_template('account_edit.html', ACCOUNT_TYPE=models.ACCOUNT_TYPE, account=account)


@money.route('/ajax/operation/edit/<aid>/<oid>', methods=['GET'])
@login_required
def ajax_operation_edit(aid, oid):
    account = api.account_get(session=g.session, aid=aid)
    operation = api.operation_get(session=g.session, oid=oid)
    return render_template('operation_edit.html', OPERATION_TYPE=models.OPERATION_TYPE, operation=operation, account=account)


@money.route('/account/list', methods=['GET'])
@login_required
def account_list():
    accounts = api.account_list(session=g.session, owner=g.user.uid)
    return render_template('account_list.html', accounts=accounts)


@money.route('/account/add', methods=['POST'])
@login_required
def account_add():
    api.account_add(session=g.session,
            owner=g.user.uid,
            name=request.form['name'],
            initial_balance=request.form['initial_balance'],
            type=request.form['type'])
    g.session.commit()
    return redirect(url_for('index'))


@money.route('/account/modify/<aid>', methods=['POST'])
@login_required
def account_modify(aid):
    account = api.account_get(session=g.session, aid=aid)
    account.name = request.form['name']
    account.initial_balance = request.form['initial_balance']
    account.type = request.form['type']
    g.session.commit()
    return redirect(url_for('account_list'))


@money.route('/account/remove/<aid>', methods=['GET'])
@login_required
def account_remove(aid):
    api.account_remove(session=g.session, aid=aid)
    g.session.commit()
    return redirect(url_for('account_list'))


@money.route('/operation/list/<aid>', methods=['GET'])
@login_required
def operation_list(aid):
    #user = user_get(session=db.session, login='pawel')
    operations = api.operation_list(session=g.session,
                                    owner=g.user.uid,
                                    account=aid,
                                    tags=None)
    return render_template('operation_list.html', aid=aid,
            operations=operations)


@money.route('/operation/save/<oid>', methods=['POST'])
@login_required
def operation_save(oid):
    g.logger.debug(request.form)
    try:
        operation = api.operation_get(session=g.session, oid=oid)
        operation.amount = request.form['amount']
        operation.type = request.form['type']
    except:
        g.logger.debug('jakas dupa')
        api.operation_add(session=g.session,
                account=request.form['aid'],
                amount=request.form['amount'],
                type=request.form['type'],
                tags=request.form['tags'])
    g.session.commit()
    return redirect(url_for('operation_list', aid=request.form['aid']))


@money.route('/operation/remove/<oid>', methods=['GET'])
@login_required
def operation_remove(oid):
    operation = api.operation_get(session=g.session, oid=oid);
    account = operation.account
    api.operation_remove(session=g.session, oid=oid)
    g.session.commit()
    return redirect(url_for('operation_list', aid=account.aid))


##
if __name__ == '__main__':
    money.run()
else:
    handler = RotatingFileHandler('/srv/money.ithaca.pl/logs/money.log', maxBytes=1048576, backupCount=1)
    handler.setLevel(logging.DEBUG)
    money.logger.addHandler(handler)
    money.debug = True
    application = money

