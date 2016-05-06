#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from wren_db import wrenDB

dbname = 'wren.db'
db = wrenDB(dbname)
db.init()
