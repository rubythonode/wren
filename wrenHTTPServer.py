#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import traceback
import re

from datetime import datetime
import dateutil.tz

from tiny_http_server import *
from gw.wren_modbus import *

TZ = 'Asia/Tokyo'
#from wrenProvider import wrenProvider

#
# strictly specifying the files to be provided.
#
_re_doc = re.compile('([\w\s~/]*)/(js/[\w+\.\-]+\.(js|html|jpg|png|css))')
__version__ = '0.1'

class WrenHTTPHandler(TinyHTTPHandler):

    def add_common_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods',
                         'GET, PUT, POST, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers',
                         'Content-Type, Content-Length')
        self.send_header('Access-Control-Max-Age', '*')
        self.send_header('Age', '0')
        self.send_header('Cache-Control', 'max-age=0, no-cache, no-store')

    def check_keymap(self, keymap):
        if not (keymap.has_key('protocol') and
            keymap.has_key('node') and
            keymap.has_key('port') and
            keymap.has_key('table') and
            keymap.has_key('address')):
            return False
        # canonicalizing
        for k in [ 'protocol', 'node', 'port', 'table' ]:
            keymap[k] = str(keymap[k])
        return True

    def do_gw_write(self, keymap, data):
        if self._is_debug(3):
            print('DEBUG: keymap=', keymap)
            print('DEBUG: data=', data)
        if not self.check_keymap(keymap):
            self.send_error_msg(400, 'ERROR: internal error, no enough config')
            return
        # protocol handler
        if keymap['protocol'] == 'MODBUS-TCP':
            if not data.has_key('value'):
                self.send_error_msg(400,
                    'ERROR: invalid data format of the request')
            # XXX should check the content of data.
            result = wren_gw_modbus_write(keymap, data['value'])
        else:
            self.send_error_msg(400,
                    'ERROR: internal error, unsupported protocol')
            return
        if not result:
            self.send_error_msg(400,
                'ERROR: internal error, gateway failed.')
            return

    def do_gw_read(self, keymap):
        if self._is_debug(3):
            print('DEBUG: keymap=', keymap)
        if not self.check_keymap(keymap):
            self.send_error_msg(400, 'ERROR: internal error, no enough config')
            return
        # protocol handler
        result = False
        if keymap['protocol'] == 'MODBUS-TCP':
            result = wren_gw_modbus_read(keymap)
        else:
            self.send_error_msg(400,
                    'ERROR: internal error, unsupported protocol')
            return
        if not result:
            self.send_error_msg(400,
                'ERROR: internal error, gateway failed.')
            return
        # get current ISO datetime.
        msg = ('{"time": "%s", "value": "%s"}' %
                (datetime.now(dateutil.tz.gettz(TZ)).isoformat(), result))
        self.send_response(200)
        self.send_header('Content-length', str(len(msg)))
        self.add_common_headers();
        self.end_headers()
        self.wfile.write(msg)
        self.wfile.write('\n')
        return

    def data_provider(self):
        ''' data provider '''
        wp = wrenProvider()
        ret, m, em = wp.execute(self.path)
        if ret != 200:
            self.send_error_msg(ret, '%s, path=%s' % (em, self.path))
            return
        #self.send_response(ret, m)
        # XXX support Accept-Encoding: gzip
        self.send_response(ret)
        self.send_header('Content-length', str(len(m)))
        self.add_common_headers();
        self.end_headers()
        self.wfile.write(m)
        self.wfile.write('\n')

    def do_HEAD(self):
        self.add_common_headers();
        self.end_headers()
        self.wfile.write('\n')

    def do_OPTIONS(self):
        self.add_common_headers();
        self.end_headers()
        self.wfile.write('\n')

    def do_GET(self):
        #
        # gateway.
        #
        if (self.server.config.has_key('keymap') and
                self.server.config['keymap'].has_key(self.path)):
            try:
                self.do_gw_read(self.server.config['keymap'][self.path])
                return
            except Exception:
                self.send_error_msg(400, 'internal error, gw failed')
                return
        #
        # data provider.
        #
        if self.path.startswith('/?'):
            try:
                if self.data_provider():
                    return
            except Exception:
                self.send_error_msg(400, 'internal error, file provider failed')
                return
        #
        # file provider.
        # it only checks whether the URL is matched with the pre-defined.
        # XXX: need to add ACL.
        #
        try:
            if self.file_provider():
                return
        except Exception:
            self.send_error_msg(400, 'internal error, file provider failed')
            return
        #
        # others
        #
        self.send_error_msg(400, 'invalid request [%s]' % self.path)
        return

    def do_PUT(self):
        #
        # gateway.
        #
        if (self.server.config.has_key('keymap') and
                self.server.config['keymap'].has_key(self.path)):
            try:
                body = json.loads(self.read_length())
            except Exception as e:
                self.send_error_msg(400, 'invalid body of the request [%s] %s'
                                    % (self.path, e))
                return
            self.do_gw_write(self.server.config['keymap'][self.path], body)
            return
        return

    def do_POST(self):
        self.send_error_msg(403, 'POST is not allowed.')
        return

if __name__ == '__main__':
    httpd = TinyHTTPServer(WrenHTTPHandler)
    httpd.run()

