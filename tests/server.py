#!/usr/bin/env python
# coding: utf-8
# author: Sergey Vasilyev <nolar@nolar.info>
#
# Fake HTTP/HTTPS server mostly for one-time requests. Designed to be used as
# a context manager ("with" operator). Listens for connections in its own thread,
# so it does not interfere with the main execution except for starting/stopping.
#
# Suggested syntax for tests:
#
#   def test_urlopen_via_ssl(self):
#       with HTTPServer(port=1234, use_ssl=True, content_body='hello'):
#           req = urllib2.urlopen('https://localhost:1234/')
#           data = req.read()
#           self.assertEqual(data, 'hello')
#
# Possibe parameters for constructor and their defaults:
#
# host          127.0.0.1   - host to listen for connections (0.0.0.0 is not recommended).
# port          8888        - port to listen for connections (1..1024 are not recommended).
# use_ssl       False       - whether it is a HTTP (False) or HTTPS (True) server.
# status_code   200         - status code (200 for OK, 404 for NotFound, etc).
# status_text   None        - status text or None for autodetection.
# content_type  text/plain  - value for Content-Type header.
# content_body  empty       - response content itself.
# encoding      utf-8       - how to encode content body; also used in Content-Type.
#

import BaseHTTPServer
import SocketServer
import os
import ssl
import threading

__all__ = ['HTTPServer']

class HTTPServer(object):
    def __init__(self, host='127.0.0.1', port=8888, use_ssl=False,
                status_code=200, status_text=None,
                content_type='text/plain', content_body='',
                encoding='utf-8'):
        super(HTTPServer, self).__init__()
        
        self.port = port
        self.host = host
        self.use_ssl = use_ssl
        self.status_code = status_code
        self.status_text = status_text
        self.content_type = content_type
        self.content_body = content_body
        self.encoding = encoding
        
        # Do not use BaseHTTPServer.HTTPServer here, since it makes hostname lookups,
        # which is not good on frequest socket binds for each test (we don't need them).
        class Server(SocketServer.TCPServer):
            allow_reuse_address = 1
            def run(self):
                self.server_bind()
                self.server_activate()
                self.serve_forever(0.1)
                self.server_close()
                #NB: server_close() is VERY IMPORTANT! SocketServer does not close its
                #NB: listening socket by default, leaving it open, which causes problems
                #NB: (such as hangings and errors 10048 WSAEADDRINUSE or 10013 WSAEACCES).
        
        class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass # omit stderr logging
            def send(self, response):
                response = unicode(response).encode(encoding)
                self.send_response(status_code, status_text)
                self.send_header('Content-Type', '%s' % (content_type))
                self.send_header('Content-Type', '%s; charset=%s' % (content_type, encoding))
                self.send_header('Content-Length', len(response))
                self.send_header('Connection', 'close')
                self.end_headers()
                self.wfile.write(response)
            def do_GET(self):
                self.send(content_body)
            def do_POST(self):
                length = self.headers.getheader('content-length')
                postdata = self.rfile.read(int(length)) if length is not None else ''
                self.send(content_body % postdata if '%s' in content_body else content_body)
        
        # Now we create socket server and controlling thread in passive mode!
        # That mean they should not open sockets or execute code here.
        self.server = Server((self.host, self.port), RequestHandler, bind_and_activate=False)
        if self.use_ssl:
            # From http://www.piware.de/2011/01/creating-an-https-server-in-python/
            # Generate: openssl req -new -x509 -days 3650 -nodes -out server.pem -keyout server.pem
            certfile = os.path.splitext(__file__)[0] + '.pem'
            self.server.socket = ssl.wrap_socket(self.server.socket, server_side=True, certfile=certfile)
        self.thread = threading.Thread(target = self.server.run)
    
    def __enter__(self):
        self.thread.start()
        return self
    
    def __exit__(self, exc_type, exc_info, exc_bt):
        self.server.shutdown()
        self.thread.join()
