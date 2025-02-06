from utils.logs import logger


class RetryAgainError(Exception):
    def __init__(self, message: str):
        logger.error(message)
        super().__init__(message)


class UnexpectedUrl(Exception):
    def __init__(self, message: str):
        message = (
            "❌ Le  bot n'est pas arrivé à la destination attendue!:",
            message,
        )
        logger.error(message)
        super().__init__(message)
