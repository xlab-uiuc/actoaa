import logging
import sys

GRAY = "\x1b[38;21m"
BLUE = "\x1b[38;5;39m"
YELLOW = "\x1b[38;5;3m"
RED = "\x1b[38;5;196m"
BOLD_RED = "\x1b[31;1m"
PLAIN = "\x1b[0m"

logger = logging.getLogger()

class MyFormatter(logging.Formatter):

    COLORS = {
        logging.DEBUG: GRAY,
        logging.INFO: BLUE,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED
    }

    def __init__(self):
        super().__init__()
        self.datefmt = "%m/%d %H:%M:%S"

    def format(self, record):
        log_fmt = "%(asctime)s " + self.COLORS.get(record.levelno) + "[%(levelname)s]" + PLAIN + " %(message)s"
        formatter = logging.Formatter(log_fmt, self.datefmt)
        return formatter.format(record)


handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(MyFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
