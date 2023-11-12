import socket
import time
from json import JSONDecodeError

from common.utils import get_args, get_message, send_message
from common.variables import (ACCOUNT_NAME, ACTION, ERROR, PRESENCE, RESPONSE,
                              TIME, USER)


def create_presence(account_name='Guest') -> dict:
    return {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }


def process_answer(message: dict) -> str:
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def main(addr: str, port: int) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((addr, port))

    msg_to_srv = create_presence()
    send_message(sock=client_socket, message=msg_to_srv)

    try:
        msg_from_srv = get_message(sock=client_socket)
        response = process_answer(message=msg_from_srv)
        print(response)
    except (ValueError, JSONDecodeError):
        print("Can't decode message from server")


if __name__ == '__main__':
    try:
        _addr, _port = get_args()
        main(_addr, _port)
    except KeyboardInterrupt:
        print(f'Server stopped')
