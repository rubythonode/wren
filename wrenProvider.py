#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os   # for __main__
import dateutil.parser
from datetime import datetime
from db.wren_db import wrenDB

from fiapy.fiapProto import fiapProto

DBNAME = 'db/wren.db'
DBTYPE = 'SQLite3'
NUM_KEY_MAXSIZE = 20

class wrenProvider():

    def execute(self, path):
        return self._parse(path)

    def _parse(self, path):
        fiap = fiapProto(strict_check=True, debug=99)
        doc = fiap.parseGETRequest(path)
        if doc == None:
            return 400, 'invalid format [%s]', 'invalid format [%s]' % (path)
        return 200, doc, None

    def _parse_old(self, path):
        strict_check = False
        try:
            #
            # TODO path should be decoded by the http encoding.
            #
            base = path.split('?')
            if len(base) != 2:
                return (400, 'invalid format [%s]' % (base),
                        'multiple queries are specified.')
            #
            params = base[1].split('&')
            #params = path.split('&')
            #
            # check and canonicalize the query
            #   valid params:
            #     c: condition id, do the task.
            #     k: key id, return the latest value.
            #        the maximum is 5 parameters.
            #
            query_keys = []
            for p in params:
                kv = p.split('=')
                if len(kv) != 2:
                    return (400, 'invalid format',
                            'multiple values are specified. %s' % (p))
                if kv[1] == '':
                    return (400, 'invalid format',
                            'null value is specified. %s' % (p))
                if kv[0] == 'c':
                    #
                    # do query with condition, and return.
                    #
                    db = wrenDB(DBNAME, DBTYPE)
                    row = db.docond(kv[1])
                    if len(row) == 0:
                        return (400, 'no record', 'no record for %s' % (p))
                    return 200, '[' + ', '.join(row) + ']', None
                elif kv[0] == 'k':
                    query_keys.append(kv[1])
                    if len(query_keys) > NUM_KEY_MAXSIZE:
                        return (400, 'too many keys',
                                'too many keys are specified. %s' % (base[1]))
                else:
                    if strict_check is True:
                        return (400, 'invalid format',
                                'unknown key is specified. %s' % (p))
                    pass
            #
            # do query with keys
            #
            if not query_keys:
                return (400, 'invalid format',
                        'no key is specified. %s' % (base[1]))

            db = wrenDB(DBNAME, DBTYPE)
            res = []
            for k in query_keys:
                row = db.select_latest(k)
                if len(row) == 0:
                    db.close()
                    return 400, 'no record', 'no record for %s' % (k)
                res.append(row[0])
            db.close()
            return 200, '[' + ', '.join(res) + ']', None
        except Exception as e:
            return 400, 'internal error', e.__str__()

if __name__ == '__main__' :
    print 'Content-Type: text/json'
    print ''
    #path = os.environ['QUERY_STRING']
    path = os.environ['REQUEST_URI']
    #
    # provider
    #
    wp = wrenProvider()
    ret, m, em = wp.execute(path)
    if ret != 200:
        print '%s, path=%s' % (em, path)
        print ret, m
    else:
        print m

