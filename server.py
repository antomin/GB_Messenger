import logging
import socket
from json import JSONDecodeError

from common.utils import get_args, get_message, send_message
from common.variables import (ACCOUNT_NAME, ACTION, ERROR, MAX_PACKAGE_LENGTH,
                              PRESENCE, RESPONSE, TIME, USER)
import logs.config_files.server_config
from exceptions import IncorrectDataReceivedError

LOG = logging.getLogger('server')


def process_client_message(message: dict) -> dict:
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message and \
            message[USER][ACCOUNT_NAME] == 'Guest':
        LOG.debug(f'Received presence message from account <{message[USER][ACCOUNT_NAME]}>')
        return {RESPONSE: 200}

    LOG.error(f'Wrong presence message from client. {message}')
    return {RESPONSE: 400, ERROR: 'Bad request'}


def main(addr: str, port: int) -> None:
    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.bind((addr, port))

    srv_socket.listen(MAX_PACKAGE_LENGTH)

    LOG.info(f'Server started on <{addr}:{port}>')

    while True:
        client_socket, client_ip = srv_socket.accept()
        LOG.debug(f'Client <{client_ip}> connected')
        try:
            msg_from_client = get_message(sock=client_socket)
            LOG.info(f'Message from client: {msg_from_client}')
            response = process_client_message(msg_from_client)
            send_message(sock=client_socket, message=response)
            LOG.debug(f'Response to client <{client_ip}> send <{response}>')
        except (IncorrectDataReceivedError, JSONDecodeError):
            LOG.error('Incorrect message from client')
        finally:
            client_socket.close()
            LOG.debug(f'Connection with client <{client_ip}> closed')


if __name__ == '__main__':
    try:
        _addr, _port = get_args()
        main(_addr, _port)
    except KeyboardInterrupt:
        LOG.info('Server stopped')
