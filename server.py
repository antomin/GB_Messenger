import logging
import socket
import time
from json import JSONDecodeError
from select import select

from common.utils import get_args, get_message, send_message
from common.variables import (ACCOUNT_NAME, ACTION, ERROR, MAX_PACKAGE_LENGTH,
                              PRESENCE, RESPONSE, TIME, USER, MESSAGE, MESSAGE_TEXT, SENDER)
import logs.config_files.server_config
from decos import log

LOG = logging.getLogger('server')


@log
def process_client_message(message: dict, client: socket, messages_lst: list) -> None:
    if (ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message and
            message[USER][ACCOUNT_NAME] == 'Guest'):
        LOG.debug(f'Received presence message from account <{message[USER][ACCOUNT_NAME]}>')
        send_message(sock=client, message={RESPONSE: 200})
    elif (ACTION in message and message[ACTION] == MESSAGE and TIME in message and MESSAGE_TEXT in message and
          ACCOUNT_NAME in message):
        messages_lst.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
    else:
        send_message(sock=client, message={RESPONSE: 400, ERROR: 'Bad request'})


def main(addr: str, port: int) -> None:
    clients = []
    messages = []

    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_socket.bind((addr, port))
    srv_socket.settimeout(0.5)

    srv_socket.listen(MAX_PACKAGE_LENGTH)

    LOG.info(f'Server started on <{addr}:{port}>')

    while True:
        try:
            client_socket, client_ip = srv_socket.accept()
        except OSError:
            pass
        else:
            LOG.debug(f'Client <{client_ip}> connected')
            clients.append(client_socket)

        recv_lst = []
        send_lst = []

        try:
            if clients:
                recv_lst, send_lst, _ = select(clients, clients, [])
        except OSError:
            pass

        if recv_lst:
            for client in recv_lst:
                try:
                    process_client_message(message=get_message(sock=client), client=client, messages_lst=messages)
                except Exception:
                    LOG.error(f'Client <{client}> disconnected')
                    clients.remove(client)

        if send_lst and messages:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }

            del messages[0]

            for client in send_lst:
                try:
                    send_message(sock=client, message=message)
                except Exception:
                    LOG.error(f'Client <{client}> disconnected')
                    clients.remove(client)


if __name__ == '__main__':
    try:
        _addr, _port, _ = get_args()
        main(_addr, _port)
    except KeyboardInterrupt:
        LOG.info('Server stopped')
