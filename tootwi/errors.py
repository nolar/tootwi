# coding: utf-8

class Error(Exception): pass

class CredentialsError(Error): pass
class CredentialsWrongError(CredentialsError): pass # HTTP 401
class CredentialsValueError(CredentialsError): pass # in case something wrong has been passed to constructor

class OperationError(Error): pass
class OperationNotPermittedError(OperationError): pass # HTTP 403
class OperationNotFoundError(OperationError): pass # HTTP 404
class OperationValueError(OperationError): pass # not a tuple or bad method/url format

class ParametersError(Error): pass
class ParametersCallbackError(ParametersError): pass

class CodecError(Error): pass
class ExternalCodecCallableError(CodecError): pass
