#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user, login_required


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
    return render_template('accounts.html')

##
@bp.route('/accounts/create', methods=['GET'])
@login_required
def account_create():
    return redirect(url_for('view.account_list'))
