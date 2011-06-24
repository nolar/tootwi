# coding: utf-8

class Error(Exception): pass

class CredentialsWrongError(Error): pass # wrong credentials or settings

class RequestError(Error): pass
class RequestAccessError(RequestError): pass # operation is not permitted
class RequestTargetError(RequestError): pass # requested method+url were not found
class RequestParametersError(RequestError): pass
class RequestCallbackError(RequestParametersError): pass # where callback is applicable (OAuth, xAuth)

#!!! errors hierarchy should respresent expected (by the developers) concept of HTTP codes:
#!!!    RequestTargetError(Code404Error)
#!!!    RequestParametersError(Code403Error)
#!!!    CredentialsWrongError(Code401Error)
#!!! On the other hand, we should make it abstract from the transport and rather implement the semantics.
