import argparse
import json
import socket
import sys
import subprocess
from ipaddress import ip_address
from pprint import pprint

from common.variables import (DEFAULT_HOST, DEFAULT_PORT, ENCODING,
                              MAX_PACKAGE_LENGTH)
from decos import log


@log
def get_args() -> tuple:
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', dest='addr', required=False, default=DEFAULT_HOST)
    parser.add_argument('-p', dest='port', required=False, default=DEFAULT_PORT)
    parser.add_argument('-u', dest='mode', required=False, default='')

    args = parser.parse_args()

    try:
        addr, port, username = args.addr, int(args.port), args.mode
        socket.inet_aton(addr)
        if port < 1024 or port > 65535:
            raise ValueError
        return addr, port, username
    except ValueError:
        print('Wrong port number.')
        sys.exit(1)
    except socket.error:
        print('Wrong IP')
        sys.exit(1)


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


def host_ping(hosts: list) -> None:
    result = {'available': [], 'not_available': []}

    for host in hosts:
        try:
            addr = ip_address(host)
        except ValueError:
            result['not_available'].append(host)
            continue
        proc = subprocess.Popen(f'ping {addr} -c 1 -t 3', shell=False, stdout=subprocess.PIPE)
        if proc.returncode == 0:
            result['available'].append(addr)
        else:
            result['not_available'].append(addr)

    pprint(result)


host_ping(['8.8.8.8', '9.9.9.9'])
