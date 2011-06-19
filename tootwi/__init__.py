# coding: utf-8
"""
Main API class to be instantiated and used. Accepts few other utulitary classes
to its constructor, such as credentials, connection, throttler, etc. For information
on utilitary objects see their corresponding modules in separate .py files.
For information on the library itself, see README files.

The developers may instantiate as many API instances with the same credentials
or connection or throttler or any other combination of parameters, as it is required
for their business logic.

The main methods to use are call() and flow(). First one (call()) is for single
all-in-one requests where you read its whole output at once. Former one (flow())
is for stream, where you read and handle data as they go, potentially infinitely.
NB: These methods have almost the same code, but there is no way to unify them,
NB: since one of them is simple callable method, whilst the other one is a generator.

There is no need to inherit this class, since it is sufficient. Though you still can.

"""

from .credentials import API, ApplicationCredentials, TemporaryCredentials, TokenCredentials, BasicCredentials
