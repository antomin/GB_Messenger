import logging
import socket
import sys
import time
from json import JSONDecodeError

import logs.config_files.client_config

from common.utils import get_args, get_message, send_message
from common.variables import (ACCOUNT_NAME, ACTION, ERROR, PRESENCE, RESPONSE,
                              TIME, USER)
from decos import log
from exceptions import ReqFieldMissingError

LOG = logging.getLogger('client')


@log
def create_presence(account_name='Guest') -> dict:
    result = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }

    LOG.debug(f'For <{account_name}> created presence message <{result}>')

    return result


@log
def process_answer(message: dict) -> str:
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError([RESPONSE])


def main(addr: str, port: int) -> None:
    LOG.info(f'Client started with host <{addr}:{port}>')
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((addr, port))
    except ConnectionRefusedError:
        LOG.error(f'Connection to <{addr}:{port}> refused')
        sys.exit(1)

    LOG.debug('Connected to server')

    msg_to_srv = create_presence()

    send_message(sock=client_socket, message=msg_to_srv)

    LOG.debug(f'Message <{msg_to_srv}> send')

    try:
        msg_from_srv = get_message(sock=client_socket)
        response = process_answer(message=msg_from_srv)
        LOG.info(f'Message from server: <{response}>')
    except JSONDecodeError:
        LOG.error("Can't decode message from server")
    except ReqFieldMissingError as error:
        LOG.error(f'No required field <{", ".join(error.missing_fields)}> in message')


if __name__ == '__main__':
    try:
        _addr, _port = get_args()
        main(_addr, _port)
        LOG.info('Client finish work')
    except KeyboardInterrupt:
        LOG.info('Client interrupt')
