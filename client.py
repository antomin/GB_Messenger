import logging
import socket
import sys
import time
from json import JSONDecodeError

import logs.config_files.client_config

from common.utils import get_args, get_message, send_message
from common.variables import (ACCOUNT_NAME, ACTION, ERROR, PRESENCE, RESPONSE,
                              TIME, USER, MESSAGE, SENDER, MESSAGE_TEXT)
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


@log
def create_message(text: str, account_name='Guest') -> dict:
    result = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: text
    }

    LOG.debug(f'New message for server: <{result}>')

    return result


def main(addr: str, port: int, mode: str) -> None:
    LOG.info(f'Client started with host <{addr}:{port}> in <{mode}> mode')
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((addr, port))
        LOG.debug('Connected to server')

        msg_to_srv = create_presence()
        send_message(sock=client_socket, message=msg_to_srv)
        LOG.debug(f'Message <{msg_to_srv}> send')

        answer = process_answer(get_message(client_socket))
        LOG.debug(f'Answer from server <{answer}>')

    except ConnectionRefusedError:
        LOG.error(f'Connection to <{addr}:{port}> refused')
        sys.exit(1)

    except JSONDecodeError:
        LOG.error("Can't decode message from server")
        sys.exit(1)

    except ReqFieldMissingError as error:
        LOG.error(f'No required field <{", ".join(error.missing_fields)}> in message')
        sys.exit(1)

    except Exception as error:
        LOG.error(f'Connection to server error: <{error}>')
        sys.exit(1)

    while True:
        try:
            if mode == 'listen':
                message = get_message(client_socket)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message:
                    print(f'{message[SENDER]}: {message[MESSAGE_TEXT]}')
                else:
                    LOG.error(f'Incorrect message from the server: {message}')

            elif mode == 'send':
                message = input('Enter your message or "!" for exit:\n')

                if message == '!':
                    client_socket.close()
                    LOG.info('Client was exit by self')
                    print('Exit')
                    sys.exit(0)

                msg_to_srv = create_message(text=message)
                send_message(sock=client_socket, message=msg_to_srv)


        except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            LOG.error('Connection to server has been interrupted')
            sys.exit(1)





    # try:
    #     msg_from_srv = get_message(sock=client_socket)
    #     response = process_answer(message=msg_from_srv)
    #     LOG.info(f'Message from server: <{response}>')
    # except JSONDecodeError:
    #     LOG.error("Can't decode message from server")
    # except ReqFieldMissingError as error:
    #     LOG.error(f'No required field <{", ".join(error.missing_fields)}> in message')


if __name__ == '__main__':
    try:
        _addr, _port, _mode = get_args()
        if _mode not in ('listen', 'send'):
            _mode = 'listen'
            LOG.warning('Unknown client mode. Client was start in <listen> mode.')
        main(_addr, _port, _mode)
        LOG.info('Client finish work')
    except KeyboardInterrupt:
        LOG.info('Client interrupt')
