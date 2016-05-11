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

    def do_gw_write(self, key, data):
        if self._is_debug(3):
            print('DEBUG: starting gateway writer for', key)
        keymap = self.server.config['keymap'][key]
        if self._is_debug(3):
            print('DEBUG: keymap=', keymap)
        if not self.check_keymap(keymap):
            self.send_error_msg(400, 'ERROR: internal error, no enough config')
            return
        # protocol handler
        if keymap['protocol'] == 'MODBUS-TCP':
            # XXX should check the content of data.
            result = wren_gw_modbus_write(keymap, data)
        else:
            self.send_error_msg(400,
                    'ERROR: internal error, unsupported protocol')
            return
        if not result['status']:
            self.send_error_msg(400, 'ERROR: %s' % result['value'])
            return
        msg = '{"status":"success"}'
        self.send_once(msg, len(msg), ctype='text/json')
        return

    def do_gw_read(self, key):
        ''' gateway function to read data.

        it is assuming that the key exists.
        '''
        if self._is_debug(3):
            print('DEBUG: starting gateway reader for', key)
        keymap = self.server.config['keymap'][key]
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
        if not result['status']:
            self.send_error_msg(400, 'ERROR: %s' % result['value'])
            return
        if keymap.has_key('adjust'):
            try:
                value = eval(str(float(result['value'])) + keymap['adjust'])
            except Exception as e:
                self.send_error_msg(400,
                    'ERROR: internal error, conversion failed.')
                return
        # get current ISO datetime.
        msg = '{"kiwi":{"version":"20140401","point":{'
        msg += ('"%s":[{"time":"%s","value":"%s"}]' %
                (key, datetime.now(dateutil.tz.gettz(TZ)).isoformat(), value))
        msg += '}}}'
        self.send_once(msg, len(msg), ctype='text/json')
        return

    def data_provider(self):
        ''' data provider '''
        wp = wrenProvider()
        ret, m, em = wp.execute(self.path)
        if ret != 200:
            self.send_error_msg(ret, '%s, path=%s' % (em, self.path))
            return True
        #self.send_response(ret, m)
        # XXX support Accept-Encoding: gzip
        self.send_response(ret)
        self.send_header('Content-length', str(len(m)))
        self.add_common_headers();
        self.end_headers()
        self.wfile.write(m)
        self.wfile.write('\n')
        return True

    def do_HEAD(self):
        self.pre_process()
        self.add_common_headers()
        self.end_headers()
        self.wfile.write('\n')

    def do_OPTIONS(self):
        self.pre_process()
        self.add_common_headers()
        self.end_headers()
        self.wfile.write('\n')

    def do_proxy_mapping(self, path):
        pass

    def do_GET(self):
        self.pre_process()
        # proxy mapping..
        #
        if (self.server.config.has_key('keymap') and
                self.server.config['keymap'].has_key(self.path)):
            do_proxy_mapping(self.path)
            return
        #
        # data provider.
        #
        if self.path.startswith('/?'):
            #
            # check base format of the path.
            #
            base = self.path.split('?')
            if len(base) != 2:
                self.send_error_msg(400,
                        'invalid format, there are multiple questions.')
            #
            # XXX currently, it only support one key.
            # XXX it should check each k=<key>.
            # XXX need to merge wrenProvider.py
            #
            params = base[1].split('&')
            for p in params:
                kv = p.split('=')
                if len(kv) != 2:
                    self.send_error_msg(400,
                        'invalid format, there are multiple values.')
                if kv[1] == '':
                    self.send_error_msg(400,
                        'invalid format, value is not specified.')
                if kv[0] == 'k':
                    if (self.server.config.has_key('keymap') and
                            self.server.config['keymap'].has_key(kv[1])):
                        try:
                            self.do_gw_read(kv[1])
                        except Exception as e:
                            self.send_error_msg(400,
                                    'internal error, gw failed, %s' % e)
                        finally:
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
        self.pre_process()
        #
        # gateway.
        #
        k = self.path[1:]
        if (self.server.config.has_key('keymap') and
                self.server.config['keymap'].has_key(k)):
            try:
                body = json.loads(self.read_length())
            except Exception as e:
                self.send_error_msg(400,
                                    'ERROR: invalid body of the request [%s] %s'
                                    % (self.path, e))
                return
            if not body.has_key('value'):
                self.send_error_msg(400,
                            'ERROR: invalid format of body [%s]' % (self.path))
            self.do_gw_write(k, body['value'])
            return
        self.send_error_msg(400, 'ERROR: invalid PUT request [%s]' % self.path)
        return

    def do_POST(self):
        self.send_error_msg(403, 'POST is not allowed.')
        return

if __name__ == '__main__':
    httpd = TinyHTTPServer(WrenHTTPHandler)
    httpd.run()

