# coding: utf-8
"""
Connections are responsible for networking activities of the API. Connection object
is usually passed to the API constructor and is used for its requests and streams.

There can be few networking layers and libraries, and the developers are free
to choose which one to use. They can also make their own connection class to
utilize their own underling library.

All derived connections must either inherit from Connection class, or at least
implement its protocol. Protocol consists of the open(request) method on the main
connection class, and read(), readline(), close() methods of returned file-like object.

Request is a signed request object as returned by credentials; it has read-only
properties to use: method, url, headers, postdata. These properties must be passed
to the remote side as is, with no modifications and extensions, since they are signed.

Dependencies must be imported on demand only, i.e. when connection is instantiated
or its method is called. There should be no dependency imports in this module itself,
since not all of them might be installed (and not all of them are really required).

"""


#??? rename connections to protocols? wrappers? connectors?

#!!! implement gzip compression. very useful for high-volume streams, etc.

#
# Base classes and their protocols.
#

class File(object):
    """
    Base file-like object class. Specific implementations can either
    derive from this class, or use their own native file-like objects.
    """
    def close(self):
        raise NotImplemented()
    def readline(self):
        raise NotImplemented()
    def read(self, length=None):
        raise NotImplemented()

class Connection(object):
    """
    Base connection class. Should never be instantiated directly.
    Descendants must implement open(request) method and return
    file-like object wth the same protocol as in File class above.
    """
    def open(self, request):
        raise NotImplemented()

#
# Connections via urllib2.
#

class urllib2Connection(Connection):
    """
    Connection implementation with urllib2 library. Uses library's native
    file-like object, since it conforms to the protocol of the File class.
    """
    def open(self, request):
        # On-demand import to avoid errors when this connection is not used.
        import urllib2, urllib

        #FIXME:
        # Rough hack to make streams work properly. Default bufsize if 8192 bytes,
        # thus causing readline() to block until all the buffer is read, even if
        # there are lines available. Bad for low-volume connections because of the lag.
        import socket;
        old_default_bufsize = socket._fileobject.default_bufsize
        socket._fileobject.default_bufsize = 0 # zero is for no buffering

        # HTTP method will be automatically choosen based on presence or absence of the postdata.
        req = urllib2.Request(request.url,
            request.postdata if request.method=='POST' else None,
            headers=request.headers)
        handle = urllib2.urlopen(req)

        #FIXME: Restore default values after file object is instantiated.
        socket._fileobject.default_bufsize = old_default_bufsize

        #!!! catch and parse HTTP errors into unified exception hierarchy of tootwi.

        return handle

#
# Connections via pycurl.
#

class pycurlConnection(Connection):
    pass

#
# Connections via httplib.
# ??? does it support streaming at all?
#

class httplibConnection(Connection):
    pass

#
# Automatically detect whcih connection to use as a default.
#??? is it stil used? or has connection became required parameter in API class?
#
DEFAULT_CONNECTION = urllib2Connection()
