import logging
import socket
import sys
import time
from json import JSONDecodeError
from threading import Thread

import logs.config_files.client_config

from common.utils import get_args, get_message, send_message
from common.variables import (ACCOUNT_NAME, ACTION, ERROR, PRESENCE, RESPONSE,
                              TIME, USER, MESSAGE, SENDER, MESSAGE_TEXT, DESTINATION, EXIT)
from decos import log
from exceptions import ReqFieldMissingError

LOG = logging.getLogger('client')


def msg_from_srv(sock: socket.socket, my_username: str) -> None:
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message and \
                    MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'\n{message[SENDER]}: {message[MESSAGE_TEXT]}')
                LOG.debug(f'New message <{MESSAGE_TEXT}> from <{SENDER}>')
            else:
                LOG.error(f'Incorrect message from server{message}')

        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, JSONDecodeError):
            LOG.error('Connection with server refused')
            break

        except Exception as error:
            LOG.error(f'Error with receiving message: <{error}>')


def user_interactive(sock: socket.socket, username: str) -> None:
    print_help()
    while True:
        command = input('Enter command: ')
        if command == 'm':
            create_message(sock=sock, account_name=username)
        elif command == 'h':
            print_help()
        elif command == 'e':
            send_message(sock=sock, message=gen_exit_msg(username))
            print('Goodbye!')
            time.sleep(1)
            LOG.info('Client exit himself')
            break
        else:
            print('Unknown command. Try again or print "h" for help.')


def print_help() -> None:
    print('Commands:\n'
          'm - send message\n'
          'h - get this help\n'
          'e - exit')


def gen_exit_msg(username: str) -> dict:
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: username
    }


@log
def create_presence(account_name) -> dict:
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
def create_message(sock: socket.socket, account_name: str) -> None:
    receiver_username = input('To user: ')
    text = input('Message: ')

    msg_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: receiver_username,
        TIME: time.time(),
        MESSAGE_TEXT: text
    }
    LOG.debug(f'New message for server: <{msg_dict}>')

    try:
        send_message(sock=sock, message=msg_dict)
    except Exception as error:
        LOG.error(f'Message not send. Error: <{error}>')


def main(addr: str, port: int, username: str) -> None:
    LOG.info(f'Client <{username}> started with host <{addr}:{port}>')
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((addr, port))
        LOG.debug('Connected to server')

        msg_to_srv = create_presence(username)
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

    RECEIVER = Thread(target=msg_from_srv, args=(client_socket, username), daemon=True)
    INTERFACE = Thread(target=user_interactive, args=(client_socket, username), daemon=True)
    RECEIVER.start()
    INTERFACE.start()

    while True:
        time.sleep(1)
        if RECEIVER.is_alive() and INTERFACE.is_alive():
            continue
        break


if __name__ == '__main__':
    try:
        _addr, _port, _username = get_args()
        if not _username:
            _username = input('Enter your username: ')
        main(_addr, _port, _username)
        LOG.info('Client finish work')
    except KeyboardInterrupt:
        LOG.info('Client interrupt')
