# coding: utf-8
"""
TooTwi is a Twitter API library with pure object-oriented approach, that gives
the developers possibility to inherit and extend its behavior as needed.
Initially it is implemented as a set of classes with carefully separated
responsibilities, which are enough usually with no need for inheritance.

This module (__init__) exports main classes for end users, so they can be seen
in IDE hinting and imported directly from tootwi module, not from its submodules.

For more information on the library and its syntax, see README and official wiki.
"""

from .credentials import API, ApplicationCredentials, TemporaryCredentials, TokenCredentials, BasicCredentials
