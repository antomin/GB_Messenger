import argparse
import json
import socket

from common.variables import DEFAULT_HOST, DEFAULT_PORT, ENCODING, MAX_PACKAGE_LENGTH
from decos import log


@log
def get_args() -> tuple:
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", dest="addr", required=False, default=DEFAULT_HOST)
    parser.add_argument("-p", dest="port", required=False, default=DEFAULT_PORT)
    parser.add_argument("-u", dest="username", required=False, default="")

    args = parser.parse_args()

    addr, port, username = args.addr, int(args.port), args.username
    return addr, port, username


@log
def get_message(sock: socket.socket) -> dict:
    raw_response = sock.recv(MAX_PACKAGE_LENGTH)
    if isinstance(raw_response, bytes):
        json_response = raw_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock: socket.socket, message: dict) -> None:
    json_message = json.dumps(message)
    raw_message = json_message.encode(ENCODING)
    sock.send(raw_message)
