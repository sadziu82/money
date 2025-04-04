#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
from config import Config
from datetime import datetime

# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


##
# engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
# db_session = scoped_session(sessionmaker(autocommit=False,
#                                         autoflush=False,
#                                         bind=engine))


## models base class
class Base(DeclarativeBase):
    pass


##
db = SQLAlchemy(model_class=Base)


##
def init_db(app, testing=False):
    ##
    import money.models
    from money import sdk

    ##
    # Base.metadata.create_all(bind=engine)
    with app.app_context():
        ##
        db.create_all()
        ##
        if testing is False:
            ##
            currency_1 = sdk.currency_create("Polski Złoty", "PLN", "zł")
            currency_2 = sdk.currency_create("Euro", "EUR", "€")
            currency_3 = sdk.currency_create("US Dollar", "USD", "$")
            currency_4 = sdk.currency_create("Pound Sterling", "GBP", "£")
            ##
            account_type_1 = sdk.account_type_create("current", 1300)
            account_type_2 = sdk.account_type_create("debit", 1500)
            account_type_3 = sdk.account_type_create("credit card", 1700)
            account_type_4 = sdk.account_type_create("installment", 2300)
            account_type_5 = sdk.account_type_create("loan", 2500)
            account_type_6 = sdk.account_type_create("mortgage", 2700)
            account_type_7 = sdk.account_type_create("savings", 3300)
            account_type_8 = sdk.account_type_create("shares", 3400)
            account_type_9 = sdk.account_type_create("securities", 3500)
            account_type_10 = sdk.account_type_create("pension plan", 3600)
            account_type_11 = sdk.account_type_create("cash", 4300)
            account_type_12 = sdk.account_type_create("money to burn", 4500)
            account_type_13 = sdk.account_type_create("rainy day", 4700)

            ##
            user_1 = sdk.user_create(login="admin", password="example!password", email="money@example.com",
                                     base_currency_uuid=currency_1.uuid)

            ##
            account_1 = sdk.account_create(
                name="PKO BP",
                currency=currency_1.uuid,
                account_type=account_type_1.uuid,
                initial_balance=3000,
                debit_limit=0,
                user_uuids=[user_1.uuid],
            )
            account_2 = sdk.account_create(
                name="Millenium",
                currency=currency_1.uuid,
                account_type=account_type_1.uuid,
                initial_balance=5000,
                debit_limit=0,
                user_uuids=[user_1.uuid],
            )
            account_3 = sdk.account_create(
                name="PKO BP EUR",
                currency=currency_2.uuid,
                account_type=account_type_1.uuid,
                initial_balance=7000,
                debit_limit=0,
                user_uuids=[user_1.uuid],
            )
            account_4 = sdk.account_create(
                name="PKO BP USD",
                currency=currency_3.uuid,
                account_type=account_type_1.uuid,
                initial_balance=1000,
                debit_limit=0,
                user_uuids=[user_1.uuid],
            )
            account_5 = sdk.account_create(
                name="XTB EUR",
                currency=currency_2.uuid,
                account_type=account_type_8.uuid,
                initial_balance=600,
                debit_limit=0,
                user_uuids=[user_1.uuid],
            )
            account_6 = sdk.account_create(
                name="XTB USD",
                currency=currency_3.uuid,
                account_type=account_type_8.uuid,
                initial_balance=700,
                debit_limit=0,
                user_uuids=[user_1.uuid],
            )
            account_7 = sdk.account_create(
                name="Hipoteka Jabłeczna",
                currency=currency_1.uuid,
                account_type=account_type_6.uuid,
                initial_balance=-150000,
                debit_limit=0,
                user_uuids=[user_1.uuid],
            )
            account_8 = sdk.account_create(
                name="Samsung A55",
                currency=currency_1.uuid,
                account_type=account_type_4.uuid,
                initial_balance=-1000,
                debit_limit=0,
                user_uuids=[user_1.uuid],
            )
            account_9 = sdk.account_create(
                name="IKZE",
                currency=currency_1.uuid,
                account_type=account_type_10.uuid,
                initial_balance=125000,
                debit_limit=0,
                user_uuids=[user_1.uuid],
            )
            account_10 = sdk.account_create(
                name="PKO BP RO",
                currency=currency_1.uuid,
                account_type=account_type_7.uuid,
                initial_balance=25000,
                debit_limit=0,
                user_uuids=[user_1.uuid],
            )

        ##
        db.session.commit()
    ##
    print("database initialized")
