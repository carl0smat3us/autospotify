import logging
from os import path

import settings

logging_datafmt = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    filename=path.join(settings.logs_paths["root"], "app.txt"),
    level=logging.ERROR,
    format="%(message)s",
    datefmt=logging_datafmt,
)  # Initialize logging for catch bugs

logger = logging.getLogger(__name__)
