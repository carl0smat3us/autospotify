import logging
from os import path

import settings


class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.msg = str(record.msg)
        return super().format(record)


log_format = "%(asctime)s: %(message)s"
log_file = path.join(settings.logs_paths["root"], settings.logs_file)

middle_level = 35

# Root logger
root_logger = logging.getLogger()
root_logger.setLevel(middle_level)

# File handler
file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
file_handler.setLevel(middle_level)
file_handler.setFormatter(CustomFormatter(log_format, datefmt=settings.logging_datefmt))
root_logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    CustomFormatter(log_format, datefmt=settings.logging_datefmt)
)
root_logger.addHandler(console_handler)

logger = logging.getLogger("app_logger")


def log_message(message: str):
    print()
    logger.log(middle_level, message)
