#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base


##
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

## models base class
Base = declarative_base()
Base.query = db_session.query_property()


##
def init_db():
    ##
    import money.models
    Base.metadata.create_all(bind=engine)
    ##
    db_session.add(money.models.User('pawel', 'pawels82', 'money@sadziu'))
    db_session.commit()
    ##
    print('database initialized')
