#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import sys
from wren_db import wrenDB

def usage():
    print 'Usage: wren_mkkey (key)'
    exit(1);

#
# main
#

if len(sys.argv) == 1:
    usage()

db = wrenDB('wren.db')
res = db.makekey(sys.argv[1])
#print res
print '    { "%s",\n      "%s" },' % (sys.argv[1], res)
