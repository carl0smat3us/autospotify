from logging import ERROR

from utils.logs import log


class RetryAgain(Exception):
    def __init__(self, message: str):
        log(message, ERROR)
        super().__init__(message)


class IpAddressError(Exception):
    def __init__(self, message: str):
        log(message, ERROR)
        super().__init__(message)


class CaptchaUnsolvable(Exception):
    def __init__(self, message: str):
        log(message, ERROR)
        super().__init__(message)
