class RetryAgainError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class UnexpectedUrl(Exception):
    def __init__(self, message: str):
        super().__init__(message)
