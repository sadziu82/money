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
import dateutil.relativedelta
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
def load_user(user_id):
    return api.user_get(session=db.session, user_id=user_id)

@money.before_request
def before_request():
    g.user = current_user
    g.db_session = db.session
    g.logger = money.logger
    today = datetime.datetime.today()
    session['today'] = datetime.datetime(today.year, today.month, today.day, 23, 59, 59)


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
        return redirect(url_for('my_account'))


@money.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('unauthenticated.html')
    login = request.form['login']
    password = request.form['password']
    user = api.user_get_by_login(session=g.db_session, login=login)
    if user is None:
        session['next'] = url_for('login')
    else:
        today = session['today']
        first_day, last_day = calendar.monthrange(today.year, today.month)
        session['next'] = url_for('index')
        session['start_date'] = datetime.datetime(today.year, today.month, 1, 0, 0, 0)
        session['end_date'] = datetime.datetime(today.year, today.month, last_day, 23, 59, 59)
        login_user(user)
    return redirect(session['next'])


@money.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    session['next'] = url_for('index')
    return redirect(session['next']) 


@money.route('/dialog/logout',methods=['GET','POST'])
def dialog_logout():
    if request.method == 'GET':
        return render_template('logout_panel.html')


@money.route('/my_account')
@login_required
def my_account():
    return render_template('my_account.html') 


@money.route('/account/list', methods=['GET'])
@login_required
def account_list():
    accounts_summary = api.account_list_with_balance(session=g.db_session,
            user_id=g.user.id)
    g.logger.info('{}'.format(accounts_summary))
    session['next'] = url_for('account_list')
    return render_template('account_list.html', accounts_summary=accounts_summary)


@money.route('/account/edit/<id>', methods=['GET'])
@login_required
def account_edit(id):
    account = api.account_get(session=g.db_session, account_id=id)
    account_type_list=api.account_type_list(session=g.db_session)
    return render_template('account_edit.html',
            account_type_list=account_type_list,
            account=account)


@money.route('/account/add', methods=['POST'])
@login_required
def account_add():
    api.account_add(session=g.db_session,
            account_type_id=request.form['account_type_id'],
            user_id=g.user.id,
            name=request.form['name'],
            initial_balance=request.form['initial_balance'],
            debit_limit=request.form['debit_limit'])
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/account/modify/<id>', methods=['POST'])
@login_required
def account_modify(id):
    account = api.account_get(session=g.db_session, account_id=id)
    account.name = request.form['name']
    account.initial_balance = request.form['initial_balance']
    account.debit_limit = request.form['debit_limit']
    account.account_type_id = request.form['account_type_id']
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/account/remove/<id>', methods=['GET'])
@login_required
def account_remove(id):
    api.account_remove(session=g.db_session, account_id=id)
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/operation/list/<account_id>', methods=['GET'])
@login_required
def operation_list_account_id(account_id):
    session['accounts'] = [account_id]
    session['next'] = url_for('operation_list')
    return redirect(session['next'])


@money.route('/operation/list', methods=['GET'])
@login_required
def operation_list():
    #start_date = datetime.datetime.today()
    #one_day = datetime.timedelta(days=10)
    #accounts = api.account_list_with_balance(session=g.db_session, owner=g.user.uid,
    #        to_date=session['start_date'] - datetime.timedelta(seconds=1))
    #balance = {}
    #for account in accounts:
    #    balance[account.aid] = account.initial_balance + account.to_date_balance
    #operations = api.operation_list(session=g.db_session,
    #        owner=g.user.uid, account=aid, tags=None,
    #        start_date=session['start_date'], end_date=session['end_date'])
    #for operation in operations:
    #    operation.balance = balance[operation.account.aid] + operation.amount
    #    balance[operation.account.aid] = balance[operation.account.aid] + operation.amount
    accounts = api.account_list_groupped(session=g.db_session, user_id=g.user.id)
    account_ids = session['accounts']
    operations = api.operation_list(session=g.db_session,
            account_ids=account_ids,
            start_date=session['start_date'],
            end_date=session['end_date'],
            last_n_operations=session.setdefault('last_n_operations', None))
    session['next'] = url_for('operation_list')
    return render_template('operation_list.html', accounts=accounts,
            account_ids=account_ids, operations=operations)


@money.route('/operation/add', methods=['POST'])
@login_required
def operation_add():
    g.logger.info(request.form)
    operation = api.operation_add(session=g.db_session,
            account_id=request.form['account_id'],
            amount=request.form['amount'],
            description=request.form['description'],
            date=request.form['date'],
            tags=request.form.getlist('tags'))
    g.db_session.commit()
    session['current_operation'] = operation.id
    return redirect(session['next'])


@money.route('/operation/modify/<id>', methods=['POST'])
@login_required
def operation_modify(id):
    g.logger.info(request.form)
    operation = api.operation_get(session=g.db_session, operation_id=id)
    operation.account_id = request.form['account_id']
    operation.amount = request.form['amount']
    operation.description = request.form['description']
    operation.date = request.form['date']
    api.set_operation_tags(session=g.db_session, operation_id=operation.id,
            tags=request.form.getlist('tags'))
    g.db_session.commit()
    session['current_operation'] = operation.id
    return redirect(session['next'])


@money.route('/operation/edit/<id>', methods=['GET'])
@login_required
def operation_edit(id):
    account_id = session['accounts'][0]
    current_account = api.account_get(session=g.db_session, account_id=account_id)
    accounts = api.account_list_groupped(session=g.db_session, user_id=g.user.id)
    try:
        operation = api.operation_get(session=g.db_session, operation_id=id)
    except NoResultFound:
        operation = None
    #tags = api.tag_list(session=g.db_session)
    tags = api.tag_list(session=g.db_session)
    return render_template('operation_edit.html', operation=operation,
            current_account=current_account, accounts=accounts, tags=tags)


@money.route('/go_one_month_back')
@login_required
def go_one_month_back():
    session['end_date'] = session['start_date'].replace(day=1, hour=0, minute=0, second=0) - datetime.timedelta(seconds=1)
    session['start_date'] = session['end_date'].replace(day=1, hour=0, minute=0, second=0)
    del session['last_n_operations']
    return redirect(session['next'])


@money.route('/current_month')
@login_required
def current_month():
    today = datetime.datetime.today()
    first_day, last_day = calendar.monthrange(today.year, today.month)
    session['start_date'] = datetime.datetime(today.year, today.month, 1, 0, 0, 0)
    session['end_date'] = datetime.datetime(today.year, today.month, last_day, 23, 59, 59)
    del session['last_n_operations']
    return redirect(session['next'])


@money.route('/last_n_operations/<n>')
@login_required
def last_n_operations(n):
    if int(n) == 0:
        del session['last_n_operations']
    else:
        session['last_n_operations'] = n
    return redirect(session['next'])


@money.route('/go_one_month_forward')
@login_required
def go_one_month_forward():
    session['start_date'] = session['start_date'] + datetime.timedelta(days=31)
    session['start_date'] = session['start_date'].replace(day=1)
    first_day, last_day = calendar.monthrange(session['start_date'].year, session['start_date'].month)
    session['end_date'] = datetime.datetime(session['start_date'].year, session['start_date'].month, last_day, 23, 59, 59)
    today = datetime.datetime.today()
    if session['start_date'] > session['today']:
        session['today'] = session['start_date']
    elif session['end_date'] > session['today']:
        session['today'] = datetime.datetime(today.year, today.month, today.day, 23, 59, 59)
    del session['last_n_operations']
    return redirect(session['next'])


@money.route('/switch_accounts/<ids>')
@login_required
def switch_accounts(ids):
    session['accounts'] = ids.split(',')
    return redirect(session['next'])


#@money.route('/start_date/<date>')
#@login_required
#def start_date(date):
#    start_date = time.strptime('{}'.format(date), '%Y-%m-%d')
#    session['start_date'] = datetime.datetime(start_date.tm_year, start_date.tm_mon,
#            start_date.tm_mday, 23, 59, 59)
#    return redirect(session['next'])
#
#
#@money.route('/end_date/<date>')
#@login_required
#def end_date(date):
#    end_date = time.strptime('{}'.format(date), '%Y-%m-%d')
#    session['end_date'] = datetime.datetime(end_date.tm_year, end_date.tm_mon,
#            end_date.tm_mday, 23, 59, 59)
#    return redirect(session['next'])


#@money.route('/ajax/edit/transfer/<tid>', methods=['GET'])
#@login_required
#def ajax_edit_transfer(tid):
#    accounts = api.account_list(session=g.db_session, owner=g.user.uid)
#    try:
#        g.logger.info(api.transfer_get(session=g.db_session, tid=tid))
#        operation_1, operation_2 = api.transfer_get(session=g.db_session, tid=tid)
#    except (NoResultFound, ValueError):
#        operation_1, operation_2 = (None, None)
#    return render_template('transfer_edit.html', accounts=accounts,
#            operation_1=operation_1, operation_2=operation_2)
#
#
#@money.route('/ajax/schedule/edit/<id>', methods=['GET'])
#@login_required
#def ajax_schedule_edit(id):
#    try:
#        schedule = api.schedule_get(session=g.db_session, id=id)
#    except NoResultFound:
#        schedule = None
#    accounts = api.account_list(session=g.db_session, owner=g.user.uid)
#    schedule_periods = api.schedule_period_list(session=g.db_session)
#    tags = api.tag_list(session=g.db_session)
#    return render_template('schedule_edit.html', schedule=schedule,
#            schedule_periods=schedule_periods, accounts=accounts, tags=tags)
#
#
#@money.route('/ajax/schedule/transfer', methods=['POST'])
#@login_required
#def ajax_schedule_transfer():
#    try:
#        schedule = api.schedule_get(session=g.db_session, id=id)
#    except NoResultFound:
#        schedule = None
#    accounts = api.account_list(session=g.db_session, owner=g.user.uid)
#    schedule_periods = api.schedule_period_list(session=g.db_session)
#    tags = api.tag_list(session=g.db_session)
#    return render_template('schedule_edit.html', schedule=schedule,
#            schedule_periods=schedule_periods, accounts=accounts, tags=tags)


#@money.route('/operation/save/<oid>', methods=['POST'])
#@login_required
#def operation_save(oid):
#    g.logger.debug(u'formularz: {}'.format(request.form))
#    try:
#        operation = api.operation_get(session=g.db_session, oid=oid)
#        operation.aid = request.form['aid']
#        operation.amount = request.form['amount']
#        operation.date = request.form['date']
#        operation.desc = request.form['desc']
#        api.set_operation_tags(session=g.db_session, oid=operation.oid,
#                tags=request.form.getlist('tags'))
#    except NoResultFound:
#        g.logger.debug(u'nowa operacja: {}'.format(request.form))
#        api.operation_add(session=g.db_session,
#                account=request.form['aid'],
#                amount=request.form['amount'],
#                date=request.form['date'],
#                desc=request.form['desc'],
#                tags=request.form.getlist('tags'))
#    g.db_session.commit()
#    return redirect(session['next'])
#
#
#@money.route('/save/transfer', methods=['POST'])
#@login_required
#def save_transfer():
#    g.logger.debug(u'formularz: {}'.format(request.form))
#    try:
#        operation = api.operation_get(session=g.db_session, oid=oid)
#        operation.aid = request.form['aid']
#        operation.amount = request.form['amount']
#        operation.date = request.form['date']
#        operation.desc = request.form['desc']
#        api.set_operation_tags(session=g.db_session, oid=operation.oid,
#                tags=request.form.getlist('tags'))
#    except NoResultFound:
#        g.logger.debug(u'nowa operacja: {}'.format(request.form))
#        api.operation_add(session=g.db_session,
#                account=request.form['aid'],
#                amount=request.form['amount'],
#                date=request.form['date'],
#                desc=request.form['desc'],
#                tags=request.form.getlist('tags'))
#    g.db_session.commit()
#    return redirect(session['next'])
#
#
#@money.route('/operation/remove/<oid>', methods=['GET'])
#@login_required
#def operation_remove(oid):
#    operation = api.operation_get(session=g.db_session, oid=oid);
#    account = operation.account
#    api.operation_remove(session=g.db_session, oid=oid)
#    g.db_session.commit()
#    return redirect(session['next'])
#
#
#@money.route('/operation/toggle_booked/<oid>', methods=['GET'])
#@login_required
#def operation_toggle_booked(oid):
#    operation = api.operation_get(session=g.db_session, oid=oid);
#    operation.booked = not operation.booked
#    g.db_session.commit()
#    return redirect(session['next'])
#
#
#@money.route('/schedule', methods=['GET'])
#@login_required
#def schedule():
#    session['next'] = url_for('schedule_list')
#    return redirect(session['next'])
#
#@money.route('/schedule/list', methods=['GET'])
#@login_required
#def schedule_list():
#    start_date = datetime.datetime.today()
#    schedules = api.schedule_list(session=g.db_session, owner=g.user.uid,
#            to_date=session['end_date'])
#    g.logger.debug(u'{}'.format(schedules))
#    schedule_list = []
#    for schedule in schedules:
#        g.logger.info(schedule)
#        s = {
#            'id': schedule.id,
#            'a1': schedule.a1,
#            'a1_name': schedule.account_1.name,
#            'a2': schedule.a2,
#            'a2_name': schedule.account_2.name,
#            'amount': schedule.amount,
#            'desc': schedule.desc,
#            'start_date': schedule.start_date,
#            'tags': schedule.tags,
#        }
#        period = schedule.period
#        while s['start_date'] <= session['end_date'].date():
#            schedule_list.append(s.copy())
#            s['start_date'] = s['start_date'] + dateutil.relativedelta.relativedelta(
#                months=period.months, days=period.days)
#    schedule_list.sort(key=lambda tup: tup['start_date'])
#    return render_template('schedule_list.html', schedule_list=schedule_list)
#
#
#@money.route('/schedule/save/<id>', methods=['POST'])
#@login_required
#def schedule_save(id):
#    if request.form['a2'] != 0:
#        external = False
#    else:
#        external = True
#    try:
#        schedule = api.schedule_get(session=g.db_session, id=id)
#        schedule.a1 = request.form['a1']
#        schedule.a2 = request.form['a2']
#        schedule.amount = request.form['amount']
#        schedule.desc = request.form['desc']
#        schedule.start_date = request.form['start_date']
#        schedule.period_id = request.form['period_id']
#        schedule.end_date = request.form['end_date']
#        schedule.tags = ', '.join(request.form.getlist('tags'))
#        schedule.external = external
#    except (NoResultFound, AttributeError):
#        g.logger.debug(u'nowa operacja: {}'.format(request.form))
#        api.schedule_add(session=g.db_session,
#                a1=request.form['a1'],
#                a2=request.form['a2'],
#                amount=request.form['amount'],
#                desc=request.form['desc'],
#                start_date=request.form['start_date'],
#                period_id=request.form['period_id'],
#                end_date=request.form['end_date'],
#                tags=', '.join(request.form.getlist('tags')),
#                external=external)
#    g.db_session.commit()
#    return redirect(session['next'])
#
#
#@money.route('/schedule/remove/<id>', methods=['GET'])
#@login_required
#def schedule_remove(id):
#    schedule = api.schedule_get(session=g.db_session, id=id);
#    account = schedule.account
#    api.schedule_remove(session=g.db_session, id=id)
#    g.db_session.commit()
#    return redirect(session['next'])


##
if __name__ == '__main__':
    money.run()
else:
    handler = RotatingFileHandler('/srv/money.ithaca.pl/logs/money.log', maxBytes=1048576, backupCount=1)
    handler.setLevel(logging.DEBUG)
    money.logger.addHandler(handler)
    money.debug = True
    application = money

