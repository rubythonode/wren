#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import argparse

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
from wrenProvider import wrenProvider

class Handler(BaseHTTPRequestHandler):
    re_doc = re.compile('([\w\s~/]*)/(js/[\w+\.\-]+\.(js|html|jpg|png|css))')

    def do_OPTIONS(self):
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        #self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        #self.send_header('Access-Control-Allow-Headers', '*)

    def do_GET(self):
        #
        # xxx need to be solved the CORS issue.
        #
        r = self.re_doc.match(self.path)
        if r:
            m = self._send_doc(r.group(2))
            return
        #
        # tiny check
        #
        #if not self.path.startswith('/?'):
        #    self.log_error('invalid request [%s]' % self.path)
        #    self._send_error(400, 'invalid format')
        #    return
        #
        # provider
        #
        wp = wrenProvider()
        ret, m, em = wp.execute(self.path)
        if ret != 200:
            self.log_error('%s, path=%s' % (em, self.path))
            self._send_error(ret, m)
            return
        #self.send_response(ret, m)
        # XXX support Accept-Encoding: gzip
        self.send_response(ret)
        self.send_header('Content-length', str(len(m)))
        self.do_OPTIONS()
        self.end_headers()
        self.wfile.write(m)
        self.wfile.write('\n')
        return

    def _send_doc(self, path):
        self.send_response(200)
        #self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        try:
            f = open(path)
        except Exception as e:
            self.log_error('no such file %s', path)
            self._send_error(400, 'no such document')
            return
        else:
            for line in f.readlines():
                self.wfile.write(line)
        f.close()

    def do_POST(self):
        self.send_error(403, 'POST is not allowed.')
        return

    def _send_error(self, code, mesg):
        self.send_error(code, mesg)
        self.end_headers()
        self.wfile.write(mesg)
        self.wfile.write('\n')
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-s', action='store', dest='server_addr', default='', help='specifies the address of the server')
    p.add_argument('-p', action='store', dest='server_port', default='18886', help='specifies the port number of the server')
    return p.parse_args()

if __name__ == '__main__':
    opt = parse_args()
    port = int(opt.server_port)

    try:
        server = ThreadedHTTPServer((opt.server_addr, port), Handler)
        print 'Starting server with %s:%s, use <Ctrl-C> to stop' % (opt.server_addr, opt.server_port)
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()


