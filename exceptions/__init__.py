from utils.logs import logger


class RetryAgainError(Exception):
    def __init__(self, message: str):
        logger.error(message)
        super().__init__(message)


class UnexpectedUrl(Exception):
    def __init__(self, message: str):
        message = (
            "❌ L'utilisateur n'est pas arrivé à la destination attendue!, destination:",
            message,
        )
        logger.error(message)
        super().__init__(message)
