import argparse
import json
import socket
import sys

from common.variables import (DEFAULT_HOST, DEFAULT_PORT, ENCODING,
                              MAX_PACKAGE_LENGTH)


def get_args() -> tuple:
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', dest='addr', required=False, default=DEFAULT_HOST)
    parser.add_argument('-p', dest='port', required=False, default=DEFAULT_PORT)

    args = parser.parse_args()

    try:
        addr, port = args.addr, int(args.port)
        socket.inet_aton(addr)
        if port < 1024 or port > 65535:
            raise ValueError
        return addr, port
    except ValueError:
        print('Wrong port number.')
        sys.exit(1)
    except socket.error:
        print('Wrong IP')
        sys.exit(1)


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