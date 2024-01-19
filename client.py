import logging
import socket
import sys
import time
from json import JSONDecodeError
from threading import Thread

import logs.config_files.client_config
from common.utils import get_args, get_message, send_message
from common.variables import (
    ACCOUNT_NAME,
    ACTION,
    DESTINATION,
    ERROR,
    EXIT,
    MESSAGE,
    MESSAGE_TEXT,
    PRESENCE,
    RESPONSE,
    SENDER,
    TIME,
    USER,
)
from decos import log
from exceptions import ReqFieldMissingError
from metaclasses import ClientVerifier

LOG = logging.getLogger("client")


class Client(metaclass=ClientVerifier):
    def __init__(self, ip_address: str, port: str, username: str):
        self.addr = ip_address
        self.port = port
        self.username = username
        self.socket = None

    def init_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.addr, self.port))
            LOG.debug("Connected to server")

            msg_to_srv = self.create_presence()
            send_message(sock=self.socket, message=msg_to_srv)
            LOG.debug(f"Message <{msg_to_srv}> send")

            answer = self.process_answer(get_message(self.socket))
            LOG.debug(f"Answer from server <{answer}>")

        except ConnectionRefusedError:
            LOG.error(f"Connection to <{self.addr}:{self.port}> refused")
            sys.exit(1)

        except JSONDecodeError:
            LOG.error("Can't decode message from server")
            sys.exit(1)

        except ReqFieldMissingError as error:
            LOG.error(f'No required field <{", ".join(error.missing_fields)}> in message')
            sys.exit(1)

        except Exception as error:
            LOG.error(f"Connection to server error: <{error}>")
            sys.exit(1)

    def start(self):
        self.init_socket()

        receiver = Thread(target=self.msg_from_srv, daemon=True)
        interface = Thread(target=self.user_interactive, daemon=True)

        receiver.start()
        interface.start()

        while True:
            time.sleep(1)
            if receiver.is_alive() and interface.is_alive():
                continue
            break

    def msg_from_srv(self) -> None:
        while True:
            try:
                message = get_message(self.socket)
                if (
                    ACTION in message
                    and message[ACTION] == MESSAGE
                    and SENDER in message
                    and DESTINATION in message
                    and MESSAGE_TEXT in message
                    and message[DESTINATION] == self.username
                ):
                    print(f"\n{message[SENDER]}: {message[MESSAGE_TEXT]}")
                    LOG.debug(f"New message <{MESSAGE_TEXT}> from <{SENDER}>")
                else:
                    LOG.error(f"Incorrect message from server{message}")

            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, JSONDecodeError):
                LOG.error("Connection with server refused")
                break

            except Exception as error:
                LOG.error(f"Error with receiving message: <{error}>")

    def user_interactive(self) -> None:
        self.print_help()

        while True:
            command = input("Enter command: ")
            if command == "m":
                self.create_message()
            elif command == "h":
                self.print_help()
            elif command == "e":
                send_message(sock=self.socket, message=self.gen_exit_msg())
                print("Goodbye!")
                time.sleep(1)
                LOG.info("Client exit himself")
                break
            else:
                print('Unknown command. Try again or print "h" for help.')

    @staticmethod
    def print_help() -> None:
        print("Commands:\n" "m - send message\n" "h - get this help\n" "e - exit")

    def gen_exit_msg(self) -> dict:
        return {ACTION: EXIT, TIME: time.time(), ACCOUNT_NAME: self.username}

    def create_presence(self) -> dict:
        result = {ACTION: PRESENCE, TIME: time.time(), USER: {ACCOUNT_NAME: self.username}}

        LOG.debug(f"For <{self.username}> created presence message <{result}>")

        return result

    @staticmethod
    def process_answer(message: dict) -> str:
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return "200 : OK"
            return f"400 : {message[ERROR]}"
        raise ReqFieldMissingError([RESPONSE])

    def create_message(self) -> None:
        receiver_username = input("To user: ")
        text = input("Message: ")

        msg_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            DESTINATION: receiver_username,
            TIME: time.time(),
            MESSAGE_TEXT: text,
        }

        LOG.debug(f"New message for server: <{msg_dict}>")

        try:
            send_message(sock=self.socket, message=msg_dict)
        except Exception as error:
            LOG.error(f"Message not send. Error: <{error}>")


def main():
    addr, port, username = get_args()

    if not username:
        username = input("Enter your username: ")

    client = Client(ip_address=addr, port=port, username=username)
    client.start()


if __name__ == "__main__":
    try:
        main()
        LOG.info("Client finish work")
    except KeyboardInterrupt:
        LOG.info("Client interrupt")
