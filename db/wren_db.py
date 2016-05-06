#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
from wren_sqlite3 import dbSQLite3
#from wren_mongodb import dbMongoDB
import random

class wrenDB():

    def __init__(self, dbname, type='SQLite3'):
        """ save the name of the database """
        self.dbname = dbname
        """ make an interface for the database """
        if type == 'SQLite3':
            self.db = dbSQLite3(dbname)
        elif type == 'MongoDB':
            self.db = dbMongoDB()
            pass
        else:
            raise ValueError

    def __exit__(self):
        self.close()

    def close(self):
        self.db.close();

    def initdb(self):
        self.db.initdb()

    def makekey(self, key):
        key_id = 'k' + self.__hash(key)
        ret = self.db.makekey(key, key_id)
        return key_id

    #
    # @return a list of the selection result in json format.
    #
    def select(self, key, cond, cursor_size=10):
        data = self.db.select(key, cond, cursor_size)
        if data == None:
            return None
        return self.__get_json(data)

    #
    # provider's interface
    #
    # @input key_id
    # @return the latest record for the key in json format.
    #
    def select_latest(self, key_id):
        data = self.db.select_latest(key_id)
        if data == None:
            return None
        return self.__get_json(data)

    def regcond(self, key, cond):
        cond_id = 'c' + self.__hash(cond)
        self.db.regcond(cond_id, key, cond)
        return cond_id

    #
    # provider's interface
    #
    # @input cond_id
    #
    def docond(self, cond_id):
        data = self.db.docond(cond_id)
        if data == None:
            return None
        return self.__get_json(data)

    def insert(self, key, ts, value):
        data = self.db.insert(key, ts, value)

    def __hash(self, key):
        h = hashlib.sha1()
        h.update(key)
        h.update(random.random().__str__())
        return h.hexdigest()

    def __get_json(self, data):
        ret = []
        for r in data:
            ret.append('{ "time": "%s", "value": "%s" }' % (r[0], r[1]))
        return ret

