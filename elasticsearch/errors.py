#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File:
"""

import json
from consts import const

# Error Code Definition
Ok = 0

#1xxx argument error
ArgumentError = 1000
SchemaFieldNotDict = 1001
ArgsNotDict = 1002
PathNotExist = 1003
PathNotDirectory = 1004
ArgumentNotExist = 1005
IndexServiceNotExist = 1006
ArgumentNotExist = 1007
IndexServiceNotExist = 1008
ArgsInvalidError = 1009
InvalidFilepathProtocol = 1010
EmptyQueryParamsError = 1011
QueryForbiddenError = 1012
UploadFileContentTypeError = 1013

#2xxx semantic error
SemanticError = 2000
ResourceAlreadyExist = 2001
ResourceNotExist = 2002
SchemaNotAdhereToLimit = 2003
DataTypeError = 2004
ValueOutOfRange = 2005
SchemaInvalidDataType = 2006
EmptyContentDataError = 2007
MultiTitleSchemaError = 2008
EmptyContentSchemaError = 2009
SchemaPropertiesAbsent = 2010
DataFormatNotAdhereToSchema = 2011
ResourceBusy = 2012
DataNotImportedError = 2013
SchemaNotSet = 2014
ProjectNotExist = 2015

#3xxx request resource limited
ResourceLimited = 3000
UploadResouceLimited = 3001
AuthFailedError = 3002
AuthOverQuotaError = 3003
TokenIdLostError = 3004

#4xxx server internal error
ServerInternalError = 4000
AsyncTaskCallError = 4001
UndefinedError = 4002
ResponseFormatError = 4003
RecallServiceCallError = 4004
FaissServiceCallError = 4005
RankServiceCallError = 4006
DocServiceCallError = 4007
MrcServiceCallError = 4008
FeatureServiceCallError = 4009
ServiceNotFoundError = 4010
WorkPipeLineError = 4011
ServiceDisableError = 4012
UncacheableError = 4013
UndefinedAuthGuardError = 4014
ParaEmbServiceCallError = 4015
MethodNotImplementedError = 4400

# Error Code Default Msg Definition
code2msg = {
    Ok: "Success",

    # 1xxx
    ArgumentError: "ArgumentError",
    SchemaFieldNotDict: "SchemaFieldNotAJsonMap",
    ArgsNotDict: "ArgumentNotDict",
    PathNotExist: "PathNotExist",
    PathNotDirectory: "PathNotDirectory",
    ArgumentNotExist: "ArgumentNotExist",
    IndexServiceNotExist: "IndexServiceNotExist",
    ArgsInvalidError: "ArgsInvalidError",
    InvalidFilepathProtocol: "InvalidFilepathProtocol",
    EmptyQueryParamsError: "EmptyQueryParamsError",
    QueryForbiddenError: "QueryForbiddenError",
    UploadFileContentTypeError: "UploadFileContentTypeError",

    # 2xxx
    SemanticError: "SemanticError",
    ResourceAlreadyExist: "ResourceAlreadyExist",
    ResourceNotExist: "ResourceNotExist",
    SchemaNotAdhereToLimit: "SchemaNotAdhereToLimit",
    DataTypeError: "DataTypeError",
    ValueOutOfRange: "ValueOutOfRange",
    SchemaInvalidDataType: "InvalidSchemaDataType",
    EmptyContentDataError: "EmptyContentDataError",
    MultiTitleSchemaError: "MultiTitleSchemaError",
    EmptyContentSchemaError: "EmptyContentSchemaError",
    SchemaPropertiesAbsent: "SchemaPropertiesAbsent",
    DataFormatNotAdhereToSchema: "DataFormatNotAdhereToSchema",
    EmptyContentDataError: "EmptyContentDataError",
    ResourceBusy: "ResourceBusy",
    DataNotImportedError: "DataNotImportedError",
    SchemaNotSet: "SchemaNotSet",

    # 3xxx
    ResourceLimited: "ResourceLimited",
    UploadResouceLimited: "UploadResouceLimited",
    AuthFailedError: "AuthFailedError",
    AuthOverQuotaError: "AuthOverQuotaError",
    TokenIdLostError: "TokenIdLostError",

    # 4xxx
    ServerInternalError: "ServerInternalError",
    AsyncTaskCallError: "AsyncTaskCallError",
    UndefinedError: "UndefinedError",
    ResponseFormatError: "ResponseFormatError",
    RecallServiceCallError: "RecallServiceCallError",
    FaissServiceCallError: "FaissServiceCallError",
    RankServiceCallError: "RankServiceCallError",
    DocServiceCallError: "DocServiceCallError",
    MrcServiceCallError: "MrcServiceCallError",
    ServiceNotFoundError: "ServiceNotFoundError",
    WorkPipeLineError: "WorkPipeLineError",
    ServiceDisableError: "ServiceDisableError",
    UncacheableError: "UncacheableError",
    MethodNotImplementedError: "NotImplemented",
    ParaEmbServiceCallError: "ParaEmbServiceCallError",
    UndefinedAuthGuardError: "UndefinedAuthGuard",
}


def get_default_code_msg(code):
    """
        1. get default code msg
        2. if not defined, get default 1000/2000/3000/4000 msg
    """
    if code in code2msg:
        return code2msg.get(code)
    else:
        return code2msg.get(round(code / 1000) * 1000, "")


class BasicException(Exception):
    """
        common exception class
        arguments:
         XXXXYY: XXXX(error code), YY(module code)
         @module: module code
         @code: status(error) code
         @msg: status description message
    """

    def __init__(self, module, code, msg=None):
        self.code = code
        self.module = module
        if msg is not None:
            if type(msg) is bytes:
                self.msg = msg.decode("utf8")
            else:
                self.msg = msg
        else:
            self.msg = get_default_code_msg(code)

    @classmethod
    def raise_if_error(cls, response):
        """raise BasicException if remote response is not Ok"""
        if type(response) == str:
            response = json.loads(response)
        if type(response) == bytes:
            response = json.loads(response.decode("utf8"))
        err_code = response.get(const.REST_CODE, ArgumentError)
        if err_code != const.REST_SUCCESS_CODE:
            raise cls.from_dict(response)

    @classmethod
    def from_dict(cls, status):
        """construct an exception from remote rpc response"""
        code = status.get(const.REST_CODE, ArgumentError)
        msg = status.get(const.REST_MSG, None)
        module = code % 100
        code = int(code / 100)
        return cls(module, code, msg)

    def to_dict(self):
        """
            convert error code and message into dict
            return: dict
        """
        res = dict()
        res["errCode"] = self.code * 100 + self.module
        res["errMsg"] = self.msg
        return res

    def __str__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)


class WebApiException(BasicException):
    """
        WebApiModuel Exception common class
        module code: 01
    """

    def __init__(self, code, msg=None):
        super(WebApiException, self).__init__(1, code, msg)


class KvstoreException(BasicException):
    """
        KvstoreException Exception common class
        module code:02
    """

    def __init__(self, code, msg=None):
        super(KvstoreException, self).__init__(2, code, msg)


class AnnManageApiException(BasicException):
    """
        AnnManageApiException Exception common class
        module code:03
    """

    def __init__(self, code, msg=None):
        super(AnnManageApiException, self).__init__(3, code, msg)


class AnnServiceException(BasicException):
    """
        AnnServiceException Exception common class
        module code:04
    """

    def __init__(self, code, msg=None):
        super(AnnServiceException, self).__init__(4, code, msg)


class SearchApiException(BasicException):
    """
        SearchApiException Exception common class
        module code:05
    """

    def __init__(self, code, msg=None, user_msg=None):
        """
        Descript: initializer
        Args:
            code: error code
            msg: exception message for log
            user_msg: if defined, user will recieve this message instead of msg
        """
        super(SearchApiException, self).__init__(5, code, msg)
        self.detail = msg
        if user_msg is not None and len(user_msg) > 0:
            self.msg = user_msg

    def log_text(self):
        """format for log"""
        error_code = code2msg[
            self.code] if self.code in code2msg else "UNKNOWN"
        error_message = self.detail if self.detail is not None else self.msg
        return "%s-%s:%s" % (error_code, str(self.code), error_message)


class AsyncTaskException(BasicException):
    """
        AsyncTaskException Exception common class
        module code:06
    """

    def __init__(self, code, msg=None):
        super(AsyncTaskException, self).__init__(6, code, msg)


class AnnControllerException(BasicException):
    """
        AnnControllerException Exception common class
        module code:07
    """

    def __init__(self, code, msg=None):
        super(AnnControllerException, self).__init__(7, code, msg)


class DemoApiException(BasicException):
    """
        DemoApiException Exception common class
        module code:08
    """

    def __init__(self, code, msg=None, user_msg=None):
        super(DemoApiException, self).__init__(8, code, msg)
        self.detail = msg
        if user_msg is not None and len(user_msg) > 0:
            self.msg = user_msg

    def log_text(self):
        """format for log"""
        error_code = code2msg[
            self.code] if self.code in code2msg else "UNKNOWN"
        error_message = self.detail if self.detail is not None else self.msg
        return "%s-%s:%s" % (error_code, str(self.code), error_message)


if __name__ == "__main__":
    print(WebApiException(ArgumentError))
    print(WebApiException(ResourceAlreadyExist))
    print(WebApiException(ResourceNotExist))
    print(KvstoreException(ResourceAlreadyExist))
    print(AnnManageApiException(ResourceAlreadyExist))
    print(AnnServiceException(ResourceAlreadyExist))
