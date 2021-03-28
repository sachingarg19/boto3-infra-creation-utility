class BaseException(Exception):
    pass


class SysExitRecommendedError(BaseException):
    pass


class InternalError(BaseException):
    pass


class SpecValidationError(BaseException):
    pass


class UploadError(BaseException):
    pass


class CLIMisconfiguredError(SysExitRecommendedError):
    pass


class InvalidRequestError(BaseException):
    pass
