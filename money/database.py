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
    from money import api

    ##
    # Base.metadata.create_all(bind=engine)
    with app.app_context():
        ##
        db.create_all()
        ##
        if testing is False:
            ##
            currency_1 = api.currency_create("Polski Złoty", "PLN", "zł")
            currency_2 = api.currency_create("Euro", "EUR", "€")
            currency_3 = api.currency_create("US Dollar", "USD", "$")
            currency_4 = api.currency_create("Pound Sterling", "GBP", "£")
            ##
            account_type_1 = api.account_type_create("current", 1300)
            account_type_2 = api.account_type_create("debit", 1500)
            account_type_3 = api.account_type_create("credit card", 1700)
            account_type_4 = api.account_type_create("installment", 2300)
            account_type_5 = api.account_type_create("loan", 2500)
            account_type_6 = api.account_type_create("mortgage", 2700)
            account_type_7 = api.account_type_create("shares", 3300)
            account_type_8 = api.account_type_create("securities", 3500)
            account_type_9 = api.account_type_create("pension plan", 3700)
            account_type_10 = api.account_type_create("cash", 4300)
            account_type_11 = api.account_type_create("money to burn", 4500)
            account_type_12 = api.account_type_create("rainy day", 4700)

            ##
            user_1 = api.user_create("pawel", "pawels82", "money@sadziu")

            ##
            account_1 = api.account_create(
                name="PKO BP",
                currency=currency_1.uuid,
                account_type=account_type_1.uuid,
                initial_balance=0,
                debit_limit=0,
                user_uuids=[user_1.uuid],
            )

        ##### ##
        ##### if testing is True:
        #####     ##
        #####     user_1 = api.user_create("pawel", "pawels82", "money@sadziu")
        #####     user_2 = api.user_create("izka", "izka81", "izka@sadziu")
        #####     ##
        #####     account_1 = api.account_create(
        #####         name="PKO BP",
        #####         currency=currency_1.uuid,
        #####         account_type=account_type_1.uuid,
        #####         initial_balance=0,
        #####         debit_limit=0,
        #####         user_uuids=[user_1.uuid],
        #####     )
        #####     account_2 = api.account_create(
        #####         name="PKO BP: USD",
        #####         currency=currency_3.uuid,
        #####         account_type=account_type_1.uuid,
        #####         initial_balance=0,
        #####         debit_limit=0,
        #####         user_uuids=[user_1.uuid],
        #####     )
        #####     account_3 = api.account_create(
        #####         name="PKO BP: EUR",
        #####         currency=currency_2.uuid,
        #####         account_type=account_type_1.uuid,
        #####         initial_balance=0,
        #####         debit_limit=0,
        #####         user_uuids=[user_1.uuid],
        #####     )
        #####     account_4 = api.account_create(
        #####         name="Millenium",
        #####         currency=currency_1.uuid,
        #####         account_type=account_type_1.uuid,
        #####         initial_balance=0,
        #####         debit_limit=0,
        #####         user_uuids=[user_1.uuid],
        #####     )
        #####     account_5 = api.account_create(
        #####         name="Car: Astra",
        #####         currency=currency_1.uuid,
        #####         account_type=account_type_5.uuid,
        #####         initial_balance=0,
        #####         debit_limit=0,
        #####         user_uuids=[user_1.uuid],
        #####     )
        #####     account_6 = api.account_create(
        #####         name="Samsung A55",
        #####         currency=currency_1.uuid,
        #####         account_type=account_type_5.uuid,
        #####         initial_balance=0,
        #####         debit_limit=0,
        #####         user_uuids=[user_1.uuid],
        #####     )
        #####     account_7 = api.account_create(
        #####         name="XTB: PLN",
        #####         currency=currency_1.uuid,
        #####         account_type=account_type_7.uuid,
        #####         initial_balance=0,
        #####         debit_limit=0,
        #####         user_uuids=[user_1.uuid],
        #####     )
        #####     account_8 = api.account_create(
        #####         name="XTB: EUR",
        #####         currency=currency_3.uuid,
        #####         account_type=account_type_7.uuid,
        #####         initial_balance=0,
        #####         debit_limit=0,
        #####         user_uuids=[user_1.uuid],
        #####     )
        #####     account_9 = api.account_create(
        #####         name="XTB: USD",
        #####         currency=currency_2.uuid,
        #####         account_type=account_type_7.uuid,
        #####         initial_balance=0,
        #####         debit_limit=0,
        #####         user_uuids=[user_1.uuid],
        #####     )
        #####     account_10 = api.account_create(
        #####         name="Jabłeczna",
        #####         currency=currency_1.uuid,
        #####         account_type=account_type_6.uuid,
        #####         initial_balance=0,
        #####         debit_limit=0,
        #####         user_uuids=[user_1.uuid],
        #####     )
        #####     ##
        #####     operation_1 = api.operation_create(
        #####         account_uuid=account_1.uuid,
        #####         amount=3000,
        #####         date=datetime.strptime("2024-05-01", "%Y-%m-%d"),
        #####         tags="tag1",
        #####         description="desc",
        #####         user_uuid=user_1.uuid,
        #####     )
        #####     operation_2 = api.operation_create(
        #####         account_uuid=account_1.uuid,
        #####         amount=-430,
        #####         date=datetime.strptime("2024-05-02", "%Y-%m-%d"),
        #####         tags="tag2",
        #####         description="desc",
        #####         user_uuid=user_1.uuid,
        #####         sibling_account_uuid=account_2.uuid,
        #####         sibling_amount=100,
        #####     )
        #####     operation_3 = api.operation_create(
        #####         account_uuid=account_2.uuid,
        #####         amount=-30,
        #####         date=datetime.strptime("2024-05-03", "%Y-%m-%d"),
        #####         tags="tag3",
        #####         description="desc",
        #####         user_uuid=user_1.uuid,
        #####         sibling_account_uuid=account_3.uuid,
        #####         sibling_amount=37,
        #####     )
        #####     operation_4 = api.operation_create(
        #####         account_uuid=account_1.uuid,
        #####         amount=-375,
        #####         date=datetime.strptime("2024-05-04", "%Y-%m-%d"),
        #####         tags="tag1",
        #####         description="desc",
        #####         user_uuid=user_1.uuid,
        #####     )
        #####     operation_5 = api.operation_create(
        #####         account_uuid=account_3.uuid,
        #####         amount=-229,
        #####         date=datetime.strptime("2024-05-05", "%Y-%m-%d"),
        #####         tags="tag1",
        #####         description="desc",
        #####         user_uuid=user_1.uuid,
        #####     )
        ##
        db.session.commit()
    ##
    print("database initialized")
