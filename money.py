#!/usr/bin/python

##
import uuid
import hashlib
import sqlalchemy
import ConfigParser

##
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import (NoResultFound)
from contextlib import contextmanager
from flask import (Flask, request, render_template, redirect,
        url_for, g, flash, session)
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import (LoginManager,
                             login_user, logout_user,
                             current_user, login_required
                             )
#from flask.forms import LoginForm
import logging
from logging.handlers import RotatingFileHandler
import time
import datetime
import calendar


# FIXME
import sys
sys.path.append('/srv/money.ithaca.pl/')

#
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
    g.db_session = db.session
    g.logger = money.logger


@money.before_request
def after_request():
    g.user = current_user
    g.db_session = db.session
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
    user = api.user_get_by_login(session=g.db_session, login=login)
    if user is None:
        session['next'] = url_for('login')
    else:
        today = datetime.datetime.today()
        first_day, last_day = calendar.monthrange(today.year, today.month)
        session['next'] = url_for('index')
        session['start_date'] = datetime.datetime(today.year, today.month, 1, 0, 0, 0)
        session['end_date'] = datetime.datetime(today.year, today.month, last_day, 23, 59, 59)
        session['today'] = datetime.datetime(today.year, today.month, today.day, 23, 59, 59)
        login_user(user)
    return redirect(session['next'])


@money.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index')) 


@money.route('/my_account')
@login_required
def my_account():
    return redirect(url_for('index')) 


@money.route('/previous_month')
@login_required
def previous_month():
    session['end_date'] = session['start_date'].replace(day=1, hour=0, minute=0, second=0) - datetime.timedelta(seconds=1)
    session['start_date'] = session['end_date'].replace(day=1, hour=0, minute=0, second=0)
    return redirect(session['next'])


@money.route('/current_month')
@login_required
def current_month():
    today = datetime.datetime.today()
    first_day, last_day = calendar.monthrange(today.year, today.month)
    session['start_date'] = datetime.datetime(today.year, today.month, 1, 0, 0, 0)
    session['end_date'] = datetime.datetime(today.year, today.month, last_day, 23, 59, 59)
    session['today'] = datetime.datetime(today.year, today.month, today.day, 23, 59, 59)
    return redirect(session['next'])


@money.route('/next_month')
@login_required
def next_month():
    session['start_date'] = session['start_date'] + datetime.timedelta(days=31)
    session['start_date'] = session['start_date'].replace(day=1)
    first_day, last_day = calendar.monthrange(session['start_date'].year, session['start_date'].month)
    session['end_date'] = datetime.datetime(session['start_date'].year, session['start_date'].month, last_day, 23, 59, 59)
    return redirect(session['next'])


@money.route('/start_date/<date>')
@login_required
def start_date(date):
    start_date = time.strptime('{}'.format(date), '%Y-%m-%d')
    session['start_date'] = datetime.datetime(start_date.tm_year, start_date.tm_mon,
            start_date.tm_mday, 23, 59, 59)
    return redirect(session['next'])


@money.route('/end_date/<date>')
@login_required
def end_date(date):
    end_date = time.strptime('{}'.format(date), '%Y-%m-%d')
    session['end_date'] = datetime.datetime(end_date.tm_year, end_date.tm_mon,
            end_date.tm_mday, 23, 59, 59)
    return redirect(session['next'])


@money.route('/account/list', methods=['GET'])
@login_required
def account_list():
    accounts = api.account_list_with_balance(session=g.db_session,
            owner=g.user.uid, to_date=session['today'])
    summary = {}
    for account in accounts:
        g.logger.info(account)
        if account.type_sort not in summary.keys():
            summary[account.type_sort] = {
                'accounts': [],
                'type_name': account.type_name,
                'to_date_balance': 0,
                'total_balance': 0,
            }
        summary[account.type_sort]['accounts'].append(api.object_to_dict(account))
        summary[account.type_sort]['to_date_balance'] = summary[account.type_sort]['to_date_balance'] + account.to_date_balance + account.initial_balance
        summary[account.type_sort]['total_balance'] = summary[account.type_sort]['total_balance'] + account.total_balance + account.initial_balance
    session['next'] = url_for('account_list')
    return render_template('account_list.html', accounts_summary=summary)


@money.route('/ajax/account/edit/<aid>', methods=['GET'])
@login_required
def ajax_account_edit(aid):
    account = api.account_get(session=g.db_session, aid=aid)
    return render_template('account_edit.html',
            account_type_list=api.account_type_list(session=g.db_session),
            account=account)


@money.route('/ajax/operation/edit/<aid>/<oid>', methods=['GET'])
@login_required
def ajax_operation_edit(aid, oid):
    account = api.account_get(session=g.db_session, aid=aid)
    accounts = api.account_list(session=g.db_session, owner=g.user.uid)
    try:
        operation = api.operation_get(session=g.db_session, oid=oid)
    except NoResultFound:
        operation = None
    tags = api.tag_list(session=g.db_session)
    return render_template('operation_edit.html', operation=operation,
            account=account, accounts=accounts, tags=tags)


@money.route('/account/add', methods=['POST'])
@login_required
def account_add():
    api.account_add(session=g.db_session,
            owner=g.user.uid,
            name=request.form['name'],
            initial_balance=request.form['initial_balance'],
            type=request.form['type'])
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/account/modify/<aid>', methods=['POST'])
@login_required
def account_modify(aid):
    account = api.account_get(session=g.db_session, aid=aid)
    account.name = request.form['name']
    account.initial_balance = request.form['initial_balance']
    account.type = request.form['type']
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/account/remove/<aid>', methods=['GET'])
@login_required
def account_remove(aid):
    api.account_remove(session=g.db_session, aid=aid)
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/operation/list/<aid>', methods=['GET'])
@login_required
def operation_list(aid):
    #user = user_get(session=db.session, login='pawel')
    start_date = datetime.datetime.today()
    one_day = datetime.timedelta(days=10)
    accounts = api.account_list_with_balance(session=g.db_session, owner=g.user.uid,
            to_date=session['start_date'] - datetime.timedelta(seconds=1))
    balance = {}
    for account in accounts:
        balance[account.aid] = account.initial_balance + account.to_date_balance
    operations = api.operation_list(session=g.db_session,
            owner=g.user.uid, account=aid, tags=None,
            start_date=session['start_date'], end_date=session['end_date'])
    for operation in operations:
        operation.balance = balance[operation.account.aid] + operation.amount
        balance[operation.account.aid] = balance[operation.account.aid] + operation.amount
    session['next'] = url_for('operation_list', aid=aid)
    return render_template('operation_list.html', aid=aid,
            operations=operations)


@money.route('/operation/save/<oid>', methods=['POST'])
@login_required
def operation_save(oid):
    g.logger.debug(u'formularz: {}'.format(request.form))
    try:
        operation = api.operation_get(session=g.db_session, oid=oid)
        operation.aid = request.form['aid']
        operation.amount = request.form['amount']
        operation.date = request.form['date']
        operation.desc = request.form['desc']
        api.set_operation_tags(session=g.db_session, oid=operation.oid,
                tags=request.form.getlist('tags'))
    except NoResultFound:
        g.logger.debug(u'nowa operacja: {}'.format(request.form))
        api.operation_add(session=g.db_session,
                account=request.form['aid'],
                amount=request.form['amount'],
                date=request.form['date'],
                desc=request.form['desc'],
                tags=request.form.getlist('tags'))
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/operation/remove/<oid>', methods=['GET'])
@login_required
def operation_remove(oid):
    operation = api.operation_get(session=g.db_session, oid=oid);
    account = operation.account
    api.operation_remove(session=g.db_session, oid=oid)
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/operation/toggle_booked/<oid>', methods=['GET'])
@login_required
def operation_toggle_booked(oid):
    operation = api.operation_get(session=g.db_session, oid=oid);
    operation.booked = not operation.booked
    g.db_session.commit()
    return redirect(session['next'])


##
if __name__ == '__main__':
    money.run()
else:
    handler = RotatingFileHandler('/srv/money.ithaca.pl/logs/money.log', maxBytes=1048576, backupCount=1)
    handler.setLevel(logging.DEBUG)
    money.logger.addHandler(handler)
    money.debug = True
    application = money

