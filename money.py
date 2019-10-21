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
import dateutil.parser
import dateutil.relativedelta
import calendar


# FIXME
import sys
sys.path.append('/srv/money/')

#
import api
import models


# this file should have something like:
# [prod]
# db_uri = mysql://money:secret_password@localhost/money
CONFIG_FILE = '/etc/money/money.cfg'
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
money.secret_key = '__put_some_random_string_here__'
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
    today = datetime.date.today()
    session['today'] = datetime.date(today.year, today.month, today.day)
    for key in ['start_date', 'end_date']:
        try:
            date = dateutil.parser.parse(session[key])
            session[key] = datetime.date(date.year, date.month, date.day)
        except KeyError:
            pass


@money.after_request
def after_request(e):
    for key in ['today', 'start_date', 'end_date']:
        try:
            session[key] = session[key].isoformat()
        except KeyError:
            pass
    g.user = current_user
    g.db_session = db.session
    g.logger = money.logger
    return e


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
        session['accounts'] = []
        session['tags'] = []
        today = session['today']
        first_day, last_day = calendar.monthrange(today.year, today.month)
        session['next'] = url_for('index')
        session['start_date'] = datetime.date(today.year, today.month, 1)
        session['end_date'] = datetime.date(today.year, today.month, last_day)
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
            user_id=g.user.id, end_date=session['today'])
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
    accounts = api.account_list_groupped(session=g.db_session, user_id=g.user.id)
    account_ids = session['accounts']
    operations = api.operation_list_with_balance(session=g.db_session,
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
    #g.logger.info(request.form)
    operation = api.operation_add(session=g.db_session,
            account_id=request.form['account_id'],
            amount=request.form['amount'],
            description=request.form['description'],
            date=request.form['date'])
    api.set_operation_tags(session=g.db_session, operation_id=operation.id,
            tags=request.form.getlist('tags'))
    g.db_session.commit()
    session['last_used_account_id'] = operation.account_id
    session['current_operation'] = operation.id
    return redirect(session['next'])


@money.route('/operation/modify/<id>', methods=['POST'])
@login_required
def operation_modify(id):
    #g.logger.info(request.form)
    operation = api.operation_get(session=g.db_session, operation_id=id)
    operation.account_id = request.form['account_id']
    operation.amount = request.form['amount']
    operation.description = request.form['description']
    operation.date = request.form['date']
    api.set_operation_tags(session=g.db_session, operation_id=operation.id,
            tags=request.form.getlist('tags'))
    g.db_session.commit()
    session['last_used_account_id'] = operation.account_id
    session['current_operation'] = operation.id
    return redirect(session['next'])


@money.route('/operation/edit/<id>', methods=['GET'])
@login_required
def operation_edit(id):
    try:
        account_id = session['last_used_account_id']
        current_account = api.account_get(session=g.db_session, account_id=account_id)
    except KeyError:
        account_id = None
        current_account = None
    accounts = api.account_list_groupped(session=g.db_session, user_id=g.user.id)
    try:
        operation = api.operation_get(session=g.db_session, operation_id=id)
    except NoResultFound:
        operation = None
    tags = api.tag_list(session=g.db_session)
    return render_template('operation_edit.html', operation=operation,
            current_account=current_account, accounts=accounts, tags=tags)


@money.route('/transfer/edit/<id>', methods=['GET'])
@login_required
def transfer_edit(id):
    try:
        current_account_id = session['accounts'][0]
    except IndexError:
        current_account_id = None
    accounts = api.account_list_groupped(session=g.db_session, user_id=g.user.id)
    try:
        transfer = api.transfer_get(session=g.db_session,
                transfer_id=id)
        operation_from = api.operation_get(session=g.db_session,
                operation_id=transfer.operation_from_id)
        operation_to = api.operation_get(session=g.db_session,
                operation_id=transfer.operation_to_id)
    except (NoResultFound, AttributeError):
        transfer = None
        operation_from = None
        operation_to = None
    tags = api.tag_list(session=g.db_session)
    return render_template('transfer_edit.html',
            current_account_id=current_account_id,
            transfer=transfer,
            operation_from=operation_from,
            operation_to=operation_to,
            accounts=accounts,
            tags=tags)


@money.route('/transfer/add', methods=['POST'])
@login_required
def transfer_add():
    #g.logger.info(request.form)
    operation_from = api.operation_add(session=g.db_session,
            account_id=request.form['account_from_id'],
            amount=-float(request.form['amount']),
            description=request.form['description'],
            date=request.form['date'])
    api.set_operation_tags(session=g.db_session, operation_id=operation_from.id,
            tags=request.form.getlist('tags'))
    operation_to = api.operation_add(session=g.db_session,
            account_id=request.form['account_to_id'],
            amount=request.form['amount'],
            description=request.form['description'],
            date=request.form['date'])
    api.set_operation_tags(session=g.db_session, operation_id=operation_to.id,
            tags=request.form.getlist('tags'))
    transfer = api.transfer_add(session=g.db_session,
            operation_from_id=operation_from.id,
            operation_to_id=operation_to.id)
    operation_from.transfer_id = transfer.id
    operation_to.transfer_id = transfer.id
    g.db_session.commit()
    session['current_operation'] = operation_from.id
    return redirect(session['next'])


@money.route('/transfer/modify/<id>', methods=['POST'])
@login_required
def transfer_modify(id):
    #g.logger.info(request.form)
    transfer = api.transfer_get(session=g.db_session, transfer_id=id)
    operation_from = api.operation_get(session=g.db_session,
            operation_id=transfer.operation_from_id)
    operation_from.account_id = request.form['account_from_id']
    operation_from.amount = -float(request.form['amount'])
    operation_from.description = request.form['description']
    operation_from.date = request.form['date']
    api.set_operation_tags(session=g.db_session,
            operation_id=transfer.operation_from_id,
            tags=request.form.getlist('tags'))
    operation_to = api.operation_get(session=g.db_session,
            operation_id=transfer.operation_to_id)
    operation_to.account_id = request.form['account_to_id']
    operation_to.amount = request.form['amount']
    operation_to.description = request.form['description']
    operation_to.date = request.form['date']
    api.set_operation_tags(session=g.db_session,
            operation_id=transfer.operation_to_id,
            tags=request.form.getlist('tags'))
    g.db_session.commit()
    session['current_operation'] = operation_from.id
    return redirect(session['next'])


@money.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    if request.method == 'POST':
        session['tags'] = request.form.getlist('tags')
    accounts = api.account_list_groupped(session=g.db_session, user_id=g.user.id)
    account_ids = session['accounts']
    operations = api.operation_list_with_balance(session=g.db_session,
            account_ids=account_ids,
            start_date=session['start_date'],
            end_date=session['end_date'],
            last_n_operations=session.setdefault('last_n_operations', None),
            tags=session['tags'])
    tags = api.tag_list(session=g.db_session)
    session['next'] = url_for('reports')
    return render_template('reports.html', accounts=accounts,
            account_ids=account_ids, operations=operations,
            tags=tags, selected_tags=session['tags'])


@money.route('/balance', methods=['GET', 'POST'])
@login_required
def balance():
    if request.method == 'POST':
        session['tags'] = request.form.getlist('tags')
    accounts = api.account_list_groupped(session=g.db_session, user_id=g.user.id)
    account_ids = session['accounts']
    balance = api.account_monthly_balance(session=g.db_session,
            account_ids=account_ids,
            start_date=session['start_date'],
            end_date=session['end_date'])
    session['next'] = url_for('balance')
    return render_template('balance.html', accounts=accounts,
            account_ids=account_ids, balance=balance)


@money.route('/go_one_month_back')
@login_required
def go_one_month_back():
    session['start_date'] = session['start_date'] + dateutil.relativedelta.relativedelta(
            months=-1)
    session['end_date'] = session['end_date'] + dateutil.relativedelta.relativedelta(
            months=-1)
    first_day, last_day = calendar.monthrange(session['end_date'].year,
            session['end_date'].month)
    session['end_date'] = datetime.date(session['end_date'].year,
            session['end_date'].month, last_day)
    try:
        del session['last_n_operations']
    except KeyError:
        pass
    return redirect(session['next'])


@money.route('/current_month')
@login_required
def current_month():
    today = datetime.date.today()
    first_day, last_day = calendar.monthrange(today.year, today.month)
    session['start_date'] = datetime.date(today.year, today.month, 1)
    session['end_date'] = datetime.date(today.year, today.month, last_day)
    try:
        del session['last_n_operations']
    except KeyError:
        pass
    return redirect(session['next'])


@money.route('/last_n_operations/<n>')
@login_required
def last_n_operations(n):
    if int(n) == 0:
        try:
            del session['last_n_operations']
        except KeyError:
            pass
    else:
        session['last_n_operations'] = n
    return redirect(session['next'])


@money.route('/go_one_month_forward')
@login_required
def go_one_month_forward():
    session['start_date'] = session['start_date'] + dateutil.relativedelta.relativedelta(
            months=1)
    session['end_date'] = session['end_date'] + dateutil.relativedelta.relativedelta(
            months=1)
    first_day, last_day = calendar.monthrange(session['end_date'].year,
            session['end_date'].month)
    session['end_date'] = datetime.date(session['end_date'].year,
            session['end_date'].month, last_day)
    try:
        del session['last_n_operations']
    except KeyError:
        pass
    return redirect(session['next'])


@money.route('/switch_accounts/<ids>')
@login_required
def switch_accounts(ids):
    if ids == 'none':
        session['accounts'] = []
    else:
        session['accounts'] = ids.split(',')
    return redirect(session['next'])


@money.route('/start_date/<date>')
@login_required
def start_date(date):
    start_date = time.strptime('{}'.format(date), '%Y-%m-%d')
    session['start_date'] = datetime.date(start_date.tm_year, start_date.tm_mon,
            start_date.tm_mday)
    try:
        del session['last_n_operations']
    except KeyError:
        pass
    return redirect(session['next'])


@money.route('/end_date/<date>')
@login_required
def end_date(date):
    end_date = time.strptime('{}'.format(date), '%Y-%m-%d')
    session['end_date'] = datetime.date(end_date.tm_year, end_date.tm_mon,
            end_date.tm_mday)
    try:
        del session['last_n_operations']
    except KeyError:
        pass
    return redirect(session['next'])


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
@money.route('/operation/remove/<operation_id>', methods=['GET'])
@login_required
def operation_remove(operation_id):
    api.operation_remove(session=g.db_session, operation_id=operation_id)
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/schedule/remove/<schedule_id>', methods=['GET'])
@login_required
def schedule_remove(schedule_id):
    api.schedule_remove(session=g.db_session, schedule_id=schedule_id)
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/transfer/remove/<transfer_id>', methods=['GET'])
@login_required
def transfer_remove(transfer_id):
    api.transfer_remove(session=g.db_session, transfer_id=transfer_id)
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/operation/toggle_booked/<operation_id>', methods=['GET'])
@login_required
def operation_toggle_booked(operation_id):
    operation = api.operation_get(session=g.db_session, operation_id=operation_id);
    operation.booked = not operation.booked
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/schedule', methods=['GET'])
@login_required
def schedule():
    session['next'] = url_for('schedule_list')
    return redirect(session['next'])

@money.route('/schedule/list', methods=['GET', 'POST'])
@login_required
def schedule_list():
    account_ids = session['accounts']
    accounts_summary = api.account_list_with_balance(session=g.db_session, user_id=g.user.id,
            end_date=session['end_date'])
    schedules = api.schedule_list(session=g.db_session, user_id=g.user.id,
            end_date=session['end_date'])
    scheduled_balance = {}
    schedule_list = []
    for schedule in schedules:
        #g.logger.info(schedule)
        s = {
            'id': schedule.id,
            'account_1_id': schedule.account_1_id,
            'account_1_name': schedule.account_1.name,
            'account_2_id': schedule.account_2_id,
            'account_2_name': schedule.account_2.name if schedule.account_2 else '',
            'amount': schedule.amount,
            'desc': schedule.desc,
            'date': schedule.start_date,
            'tags': schedule.tags,
        }
        period = schedule.schedule_period
        try:
            if request.method == 'POST' and request.form[s['id']]:
                s['checked'] = ' checked'
        except KeyError:
            s['checked'] = ''
        ##
        if schedule.end_date:
            s['end_date'] = schedule.end_date
        else:
            s['end_date'] = session['end_date']
        ##
        while s['date'] <= session['end_date'] and s['date'] <= s['end_date']:
            schedule_list.append(s.copy())
            s['date'] = s['date'] + dateutil.relativedelta.relativedelta(
                months=period.months, days=period.days)
            try:
                if request.method == 'POST' and request.form[s['id']]:
                    if s['account_2_id']:
                        scheduled_balance[s['account_1_id']] = scheduled_balance.setdefault(s['account_1_id'], 0) - s['amount']
                        scheduled_balance[s['account_2_id']] = scheduled_balance.setdefault(s['account_2_id'], 0) + s['amount']
                    else:
                        scheduled_balance[s['account_1_id']] = scheduled_balance.setdefault(s['account_1_id'], 0) + s['amount']
            except KeyError:
                pass
            if period.months == 0 and period.days == 0:
                break
    schedule_list.sort(key=lambda s: s['date'])
    if request.method == 'POST':
        for account_type_group in accounts_summary:
            for account in accounts_summary[account_type_group]['accounts']:
                try:
                    account['total_balance'] = account['total_balance'] + scheduled_balance[account['id']]
                    accounts_summary[account_type_group]['total_balance'] = accounts_summary[account_type_group]['total_balance'] + scheduled_balance[account['id']]
                except KeyError:
                    pass
    ##
    session['next'] = url_for('schedule_list')
    #g.logger.debug(u'{}'.format(scheduled_balance))
    return render_template('schedule_list.html', accounts_summary=accounts_summary,
            account_ids=account_ids, schedule_list=schedule_list)


@money.route('/schedule/transfer', methods=['POST'])
@login_required
def schedule_transfer():
    for schedule_id in request.form:
        max_date = max(request.form.getlist(schedule_id))
        api.schedule_transfer(session=g.db_session, schedule_id=schedule_id,
                max_date=max_date)
        g.logger.info('{}: {}'.format(schedule_id, max_date))
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/schedule/transfer_next_week', methods=['GET'])
@login_required
def schedule_transfer_next_week():
    for schedule_id in request.form:
        max_date = max(request.form.getlist(schedule_id))
        api.schedule_transfer(session=g.db_session, schedule_id=schedule_id,
                max_date=max_date)
        g.logger.info('{}: {}'.format(schedule_id, max_date))
    g.db_session.commit()
    return redirect(session['next'])


@money.route('/schedule/edit/<id>', methods=['GET'])
@login_required
def schedule_edit(id):
    try:
        account_id = session['last_used_account_id']
        current_account = api.account_get(session=g.db_session, account_id=account_id)
    except KeyError:
        account_id = None
        current_account = None
        #accounts = api.account_list(session=g.db_session, user_id=g.user.id)
        #current_account = accounts[0]
        #account_id = current_account.id
    accounts = api.account_list_groupped(session=g.db_session, user_id=g.user.id)
    schedule_periods = api.schedule_period_list(session=g.db_session)
    try:
        schedule = api.schedule_get(session=g.db_session, schedule_id=id)
    except NoResultFound:
        schedule = None
    tags = api.tag_list(session=g.db_session)
    return render_template('schedule_edit.html',
            schedule=schedule, schedule_periods=schedule_periods,
            current_account=current_account, accounts=accounts, tags=tags)


@money.route('/schedule/add', methods=['POST'])
@login_required
def schedule_add():
    #g.logger.info(request.form)
    schedule = api.schedule_add(session=g.db_session,
            account_1_id=request.form['account_1_id'],
            account_2_id=request.form['account_2_id']
                         if request.form['account_2_id'] != ''
                         else None,
            amount=request.form['amount'],
            desc=request.form['desc'],
            schedule_period_id=request.form['schedule_period_id'],
            start_date=request.form['start_date'],
            end_date=request.form['end_date']
                     if request.form['end_date'] != ''
                     else None)
    api.set_schedule_tags(session=g.db_session, schedule_id=schedule.id,
            tags=request.form.getlist('tags'))
    g.db_session.commit()
    session['last_used_account_id'] = schedule.account_1_id
    session['current_schedule'] = schedule.id
    session['next'] = url_for('schedule_list')
    return redirect(session['next'])


@money.route('/schedule/modify/<id>', methods=['POST'])
@login_required
def schedule_modify(id):
    #g.logger.info(request.form)
    schedule = api.schedule_get(session=g.db_session, schedule_id=id)
    schedule.account_1_id=request.form['account_1_id']
    schedule.account_2_id=request.form['account_2_id'] \
                          if request.form['account_2_id'] != '' \
                          else None
    schedule.amount=request.form['amount']
    schedule.desc=request.form['desc']
    schedule.schedule_period_id=request.form['schedule_period_id']
    schedule.start_date=request.form['start_date']
    schedule.end_date=request.form['end_date'] \
                      if request.form['end_date'] != '' \
                      else None
    api.set_schedule_tags(session=g.db_session, schedule_id=schedule.id,
            tags=request.form.getlist('tags'))
    g.db_session.commit()
    session['last_used_account_id'] = schedule.account_1_id
    session['current_schedule'] = schedule.id
    return redirect(session['next'])


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
    handler = RotatingFileHandler('/srv/money/logs/money.log', maxBytes=1048576, backupCount=1)
    handler.setLevel(logging.DEBUG)
    money.logger.addHandler(handler)
    money.debug = True
    application = money

