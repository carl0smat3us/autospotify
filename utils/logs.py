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

logging.basicConfig(
    stream=open(log_file, 'a', encoding='utf-8'),
    level=middle_level,
    format=log_format,
    datefmt=settings.logging_datefmt,
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(CustomFormatter(log_format))

root_logger = logging.getLogger()
root_logger.addHandler(console_handler)

logger = logging.getLogger("app_logger")

def log_message(message: str):
    logger.log(middle_level, message)
