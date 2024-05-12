#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user

##
from money.database import db_session
from money.exc import UserNotValid
from money.api import user_validate, user_fetch


#
bp = Blueprint('auth', __name__)

##
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

##
@login_manager.user_loader
def load_user(user_uuid):
    return user_fetch(uuid=user_uuid)


##
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ## get params
        username = request.form['username']
        password = request.form['password']
        ##
        try:
            user = user_validate(login=username, password=password)
            login_user(user)
            return redirect(url_for('view.index'))
        except UserNotValid:
            flash('incorrect username or password!')

    ##
    return render_template('login.html')

##
@bp.route('/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('auth.login'))
