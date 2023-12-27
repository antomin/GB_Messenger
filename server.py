import logging
import socket
from select import select

from common.utils import get_args, get_message, send_message
from common.variables import (ACCOUNT_NAME, ACTION, ERROR, MAX_PACKAGE_LENGTH,
                              PRESENCE, RESPONSE, TIME, USER, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT)
from decos import log

LOG = logging.getLogger('server')


@log
def process_client_message(message: dict, client: socket, messages_lst: list, clients: list, names: dict) -> None:
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
        LOG.debug(f'Received presence message from account <{message[USER][ACCOUNT_NAME]}>')
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(sock=client,  message={RESPONSE: 200})
        else:
            send_message(
                sock=client,
                message={RESPONSE: 400, ERROR: f'Username <{message[USER][ACCOUNT_NAME]}> is busy'}
            )
            clients.remove(client)
            client.close()

    elif (ACTION in message and message[ACTION] == MESSAGE and TIME in message and DESTINATION in message and
          SENDER in message and MESSAGE_TEXT in message):
        messages_lst.append(message)

    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]

    else:
        send_message(sock=client, message={RESPONSE: 400, ERROR: 'Bad request'})


def process_message(message: dict, names: dict, send_lst: list):
    if message[DESTINATION] in names and names[message[DESTINATION]] in send_lst:
        send_message(sock=names[message[DESTINATION]], message=message)
        LOG.info(f'Client <{message[SENDER]}> send message to <{message[DESTINATION]}>')

    elif message[DESTINATION] in names and names[message[DESTINATION]] not in send_lst:
        raise ConnectionError

    else:
        LOG.info(f'User <{message[DESTINATION]}> offline')


def main(addr: str, port: int) -> None:
    clients = []
    messages = []
    names = {}

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
                    process_client_message(message=get_message(sock=client), client=client, messages_lst=messages,
                                           names=names, clients=clients)
                except Exception as error:
                    LOG.error(f'Client <{client}> disconnected: {error}')
                    clients.remove(client)

        for msg in messages:
            try:
                process_message(message=msg, names=names, send_lst=send_lst)
            except Exception as error:
                LOG.info(f'Client <{msg[DESTINATION]}> was disconnected: {error}')
                clients.remove(names[msg[DESTINATION]])
                del names[msg[0]]

        messages.clear()


if __name__ == '__main__':
    try:
        _addr, _port, _ = get_args()
        main(_addr, _port)
    except KeyboardInterrupt:
        LOG.info('Server stopped')
