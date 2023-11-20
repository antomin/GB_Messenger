import logging
import os.path
import sys

from common.variables import BASE_DIR

_FORMATTER = logging.Formatter('%(asctime)-30s %(levelname)-10s %(filename)-15s %(message)s')
_FILE_PATH = os.path.join(BASE_DIR, 'logs', 'log_files', 'client.log')

_STREAM_HANDLER = logging.StreamHandler(sys.stderr)
_STREAM_HANDLER.setLevel(logging.INFO)
_STREAM_HANDLER.setFormatter(_FORMATTER)

_FILE_HANDLER = logging.FileHandler(_FILE_PATH, encoding='utf-8')
_FILE_HANDLER.setLevel(logging.ERROR)
_FILE_HANDLER.setFormatter(_FORMATTER)


_LOGGER = logging.getLogger('client')
_LOGGER.addHandler(_STREAM_HANDLER)
_LOGGER.addHandler(_FILE_HANDLER)
_LOGGER.setLevel(logging.INFO)

