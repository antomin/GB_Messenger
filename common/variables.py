import os

DEFAULT_PORT = 7777
DEFAULT_HOST = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
SENDER = 'sender'
MESSAGE_TEXT = 'message_text'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
