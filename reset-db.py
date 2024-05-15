#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
from money.database import init_db
from money import create_app


##
if __name__ == "__main__":
    app = create_app()
    init_db(app)
