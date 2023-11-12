import socket
from json import JSONDecodeError

from common.utils import get_args, get_message, send_message
from common.variables import (ACCOUNT_NAME, ACTION, ERROR, MAX_PACKAGE_LENGTH,
                              PRESENCE, RESPONSE, TIME, USER)


def process_client_message(message: dict) -> dict:
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message and \
            message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {RESPONSE: 400, ERROR: 'Bad request'}


def main(addr: str, port: int) -> None:
    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.bind((addr, port))

    srv_socket.listen(MAX_PACKAGE_LENGTH)

    print(f'Server started on <{addr}:{port}>')

    while True:
        client_socket, client_ip = srv_socket.accept()
        try:
            msg_from_client = get_message(sock=client_socket)
            print(msg_from_client)
            response = process_client_message(msg_from_client)
            send_message(sock=client_socket, message=response)
        except (ValueError, JSONDecodeError):
            print('Incorrect message from client')
        finally:
            client_socket.close()


if __name__ == '__main__':
    try:
        _addr, _port = get_args()
        main(_addr, _port)
    except KeyboardInterrupt:
        print(f'Server stopped')
