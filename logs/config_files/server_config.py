import logging
import os.path
import sys
from logging.handlers import TimedRotatingFileHandler

from common.variables import BASE_DIR

_FORMATTER = logging.Formatter('%(asctime)-30s %(levelname)-10s %(filename)-15s %(message)s')
_FILE_PATH = os.path.join(BASE_DIR, 'logs', 'log_files', 'server.log')

_STREAM_HANDLER = logging.StreamHandler(sys.stderr)
_STREAM_HANDLER.setLevel(logging.DEBUG)
_STREAM_HANDLER.setFormatter(_FORMATTER)

_FILE_HANDLER = TimedRotatingFileHandler(_FILE_PATH, encoding='utf-8', interval=1, when='midnight')
_FILE_HANDLER.setLevel(logging.ERROR)
_FILE_HANDLER.setFormatter(_FORMATTER)


_LOGGER = logging.getLogger('server')
_LOGGER.addHandler(_STREAM_HANDLER)
_LOGGER.addHandler(_FILE_HANDLER)
_LOGGER.setLevel(logging.DEBUG)
