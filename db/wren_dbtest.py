#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from wren_db import wrenDB
import dateutil.parser
from datetime import timedelta
import random
import time as _time
import sys, os

def usage():
    print 'usage: this new [mem]'
    print '       this reuse key_id cond_id'
    exit(1)

f_init = False
dbname = 'wren.db'
cond_id = None

if len(sys.argv) <= 1:
    usage()

if sys.argv[1] == 'new':
    f_init = True
    if len(sys.argv) == 3:
        if sys.argv[2] == 'mem':
            dbname = ':memory:'
        else:
            usage()
elif sys.argv[1] == 'reuse':
    f_init = False
    if len(sys.argv) != 4:
        usage()
    key_id = sys.argv[2]
    cond_id = sys.argv[3]
else:
    usage()

if f_init is True and dbname != ':memory:':
    os.remove(dbname)

print 'initialize:', f_init
print 'dbname:', dbname

key = 'http://fiap.example.org/home/living/temperature'

db = wrenDB(dbname, type='SQLite3')

if f_init:
    print 'initialize the wren database [%s]' % (dbname)
    db.initdb()

    key_id = db.makekey(key)
    print 'create %s for %s' % (key_id, key)

    print 'generate a bunch of time sequencial data (temperature)'
    dt = dateutil.parser.parse('2014-10-17T08:00:00+0900')
    dt = dt.replace(tzinfo=dateutil.tz.gettz('Asia/Tokyo'))
    for i in range(0, 40):
        dt -= timedelta(minutes=5)
        value = '%.1f' % (random.random() * 45 - 5)   # temperature
        ts = dt.strftime('%Y-%m-%dT%H:%M:%S%z')
        print '%s %s' % (ts, value)
        db.insert(key, ts, value)

print
print 'select one of data'
cond = '{ "time": { "$gt" : "2014-10-17T07:50:00+0900" } }'
row = db.select(key, cond)
if len(row) > 0:
    print '{'
    for r in row:
        print r
    print '}'

print
print 'select the latest one'
row = db.select_latest(key_id)
if len(row) > 0:
    print '{'
    for r in row:
        print r
    print '}'

print
print 'select a range of data'
cond = {
    "$and": [
        { "time": { "$gt" : "2014-10-17T07:00:00+0900" } },
        { "time": { "$lte": "2014-10-17T08:00:00+0900" } } ] }
row = db.select(key, cond, cursor_size=5)
if len(row) > 0:
    print '{'
    for r in row:
        print r
    print '}'

if f_init:
    print
    print 'register a condition'
    cond = '''{
        "$or": [
            { "time": { "$lt": "2014-10-17T07:00:00+0900" } },
            { "time": { "$gt": "2014-10-17T07:40:00+0900" } } ] }'''
    cond_id = db.regcond(key, cond)

print
print 'select a range of data with a cond_id', cond_id
row = db.docond(cond_id)
if len(row) > 0:
    print '{'
    for r in row:
        print r
    print '}'
