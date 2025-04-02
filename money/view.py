#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_required

from datetime import datetime

##
from money.exc import UserNotValid, AccountError, OperationError
from money.database import db
from money import api

##
bp = Blueprint('view', __name__)

##
@bp.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')

##
@bp.route('/accounts', methods=['GET'])
@login_required
def account_list():
    ##
    groupped_account_list = api.account_list_groupped_with_balance(user_uuid=current_user.uuid,
                                                                   today_date=datetime.today())
    return render_template('accounts.html', groupped_account_list=groupped_account_list)

##
@bp.route('/accounts/create', methods=['GET', 'POST'])
@login_required
def account_create():
    if request.method == 'POST':
        ## get params
        name = request.form['name']
        currency = request.form['currency']
        account_type = request.form['account_type']
        initial_balance = request.form['initial_balance']
        debit_limit = request.form['debit_limit']
        ##
        try:
            account = api.account_create(name=name, currency=currency, account_type=account_type,
                                         initial_balance=initial_balance, debit_limit=debit_limit,
                                         user_uuids=[current_user.uuid])
            db.session.commit()
            return redirect(url_for('view.account_list'))
        except UserNotValid:
            flash('account creation error')

    ##
    currency_list = api.currency_list()
    account_type_list = api.account_type_list()
    return render_template('account_create.html', currency_list=currency_list, account_type_list=account_type_list)

##
@bp.route('/accounts/edit', methods=['GET', 'POST'])
@login_required
def account_edit():
    if request.method == 'POST':
        ## get params
        uuid = request.form['uuid']
        name = request.form['name']
        currency_uuid = request.form['currency_uuid']
        account_type_uuid = request.form['account_type_uuid']
        initial_balance = request.form['initial_balance']
        debit_limit = request.form['debit_limit']
        ##
        try:
            account = api.account_update(uuid=uuid, name=name,
                                         currency_uuid=currency_uuid, account_type_uuid=account_type_uuid,
                                         initial_balance=initial_balance, debit_limit=debit_limit)
                                         
            db.session.commit()
            return redirect(url_for('view.account_list'))
        except UserNotValid:
            flash('account update error')

    ##
    uuid = request.args.get('uuid')
    account = api.account_fetch(uuid)
    ##
    currency_list = api.currency_list()
    account_type_list = api.account_type_list()
    ##
    return render_template('account_edit.html', account=account, currency_list=currency_list,
                           account_type_list=account_type_list)

##
@bp.route('/accounts/delete', methods=['GET', 'POST'])
@login_required
def account_delete():
    ##
    if request.method == 'POST':
        ## get params
        uuid = request.form['uuid']
        ##
        try:
            account = api.account_delete(uuid=uuid)
            db.session.commit()
            return redirect(url_for('view.account_list'))
        except UserNotValid:
            flash('account deletion error')

    ## get params
    uuid = request.args.get('uuid')
    account = api.account_fetch(uuid=uuid, user_uuid=current_user.uuid)
    user_account_list = api.user_account_list(account_uuid=account.uuid)
    return render_template('account_delete.html', account=account, user_account_list=user_account_list)


##
@bp.route('/operation/list', methods=['GET'])
@login_required
def operation_list():
    ##
    operation_list = api.operation_list_with_balance(account_uuids=[], user_uuid=current_user.uuid)
    #operation_list = api.operation_list(account_uuids=[])
    return render_template('operation_list.html', operation_list=operation_list)


##
@bp.route('/operation/create', methods=['GET', 'POST'])
@login_required
def operation_create():
    if request.method == 'POST':
        try:
            params = request.form.to_dict()
            params['amount'] = float(params['amount'])
            params['sibling_account_uuid'] = None if params['sibling_account_uuid'] == 'None' else params['sibling_account_uuid']
            params['sibling_amount'] = float(params['sibling_amount'] or 0)
            params['date'] = datetime.strptime(params['date'], '%Y-%m-%d')

            operation = api.operation_create(**params, user_uuid=current_user.uuid)
            db.session.commit()
            return redirect(url_for('view.operation_list'))
        except OperationError:
            flash('operation create error')

    ##
    action = request.args.get('action')
    uuid = request.args.get('uuid')
    account_list = api.account_list(user_uuid=current_user.uuid)
    ##
    return render_template('operation_item.html', action='create', account_list=account_list)


##
@bp.route('/operation/update', methods=['GET', 'POST'])
@login_required
def operation_update():
    if request.method == 'POST':
        try:
            params = request.form.to_dict()
            params['amount'] = float(params['amount'])
            params['sibling_account_uuid'] = None if params['sibling_account_uuid'] == 'None' else params['sibling_account_uuid']
            params['sibling_amount'] = float(params['sibling_amount'] or 0)
            params['date'] = datetime.strptime(params['date'], '%Y-%m-%d')

            operation = api.operation_update(**params, user_uuid=current_user.uuid)
            db.session.commit()
            return redirect(url_for('view.operation_list'))
        except OperationError:
            flash('operation create error')

    ##
    action = request.args.get('action')
    uuid = request.args.get('uuid')
    operation = api.operation_fetch(uuid=uuid, user_uuid=current_user.uuid)
    account_list = api.account_list(user_uuid=current_user.uuid)
    ##
    return render_template('operation_item.html', action='update', operation=operation, account_list=account_list)


##
@bp.route('/operation/delete', methods=['GET', 'POST'])
@login_required
def operation_delete():
    if request.method == 'POST':
        try:
            operation = api.operation_delete(**(request.form), user_uuid=current_user.uuid)
            db.session.commit()
            return redirect(url_for('view.operation_list'))
        except OperationError:
            flash('operation delete error')

    ##
    action = request.args.get('action')
    uuid = request.args.get('uuid')
    operation = api.operation_fetch(uuid=uuid, user_uuid=current_user.uuid)
    account_list = api.account_list(user_uuid=current_user.uuid)
    ##
    return render_template('operation_item.html', action='delete', operation=operation, account_list=account_list)


##
@bp.route('/operation/book', methods=['GET'])
@login_required
def operation_book():
    ##
    uuid = request.args.get('uuid')
    api.operation_toggle(uuid=uuid, user_uuid=current_user.uuid)
    db.session.commit()
    ##
    return redirect(url_for('view.operation_list'))
