import logging
import socket
from select import select

import logs.config_files.server_config
from common.utils import get_args, get_message, send_message
from common.variables import (
    ACCOUNT_NAME,
    ACTION,
    DESTINATION,
    ERROR,
    EXIT,
    MAX_PACKAGE_LENGTH,
    MESSAGE,
    MESSAGE_TEXT,
    PRESENCE,
    RESPONSE,
    SENDER,
    SERVER_DB_URL,
    TIME,
    USER,
)
from db_api import ServerDatabase
from descriptors import IPAddress, Port
from metaclasses import ServerVerifier

LOG = logging.getLogger("server")

server_db = ServerDatabase(db_url=SERVER_DB_URL)


class Server(metaclass=ServerVerifier):
    port = Port()
    addr = IPAddress()

    def __init__(self, ip_address: str, port: int):
        self.addr = ip_address
        self.port = port
        self.clients = []
        self.messages = []
        self.names = {}
        self.socket = None

    def init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.addr, self.port))
        self.socket.settimeout(0.5)

        self.socket.listen(MAX_PACKAGE_LENGTH)

    def start(self):
        self.init_socket()
        LOG.info(f"Server started on <{self.addr}:{self.port}>")

        while True:
            try:
                client_socket, client_ip = self.socket.accept()
            except OSError:
                pass
            else:
                LOG.debug(f"Client <{client_ip}> connected")
                self.clients.append(client_socket)

            recv_lst = []
            send_lst = []

            try:
                if self.clients:
                    recv_lst, send_lst, _ = select(self.clients, self.clients, [])
            except OSError:
                pass

            if recv_lst:
                for client in recv_lst:
                    try:
                        self.process_client_message(
                            message=get_message(sock=client),
                            client=client,
                            messages_lst=self.messages,
                            names=self.names,
                            clients=self.clients,
                        )
                    except Exception as error:
                        LOG.error(f"Client <{client}> disconnected: {error}")
                        self.clients.remove(client)

            for msg in self.messages:
                try:
                    self.process_message(message=msg, names=self.names, send_lst=send_lst)
                except Exception as error:
                    LOG.info(f"Client <{msg[DESTINATION]}> was disconnected: {error}")
                    self.clients.remove(self.names[msg[DESTINATION]])
                    server_db.user_logout(msg[DESTINATION])
                    del self.names[msg[0]]

            self.messages.clear()

    @staticmethod
    def process_client_message(
        message: dict, client: socket.socket, messages_lst: list, clients: list, names: dict
    ) -> None:
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            LOG.debug(f"Received presence message from account <{message[USER][ACCOUNT_NAME]}>")
            if message[USER][ACCOUNT_NAME] not in names.keys():
                names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                server_db.user_login(
                    username=message[USER][ACCOUNT_NAME], ip_address=client_ip, port=client_port
                )
                send_message(sock=client, message={RESPONSE: 200})
            else:
                send_message(
                    sock=client,
                    message={RESPONSE: 400, ERROR: f"Username <{message[USER][ACCOUNT_NAME]}> is busy"},
                )
                clients.remove(client)
                client.close()

        elif (
            ACTION in message
            and message[ACTION] == MESSAGE
            and TIME in message
            and DESTINATION in message
            and SENDER in message
            and MESSAGE_TEXT in message
        ):
            messages_lst.append(message)

        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            server_db.user_logout(username=message[ACCOUNT_NAME])
            clients.remove(names[message[ACCOUNT_NAME]])
            names[message[ACCOUNT_NAME]].close()
            del names[message[ACCOUNT_NAME]]

        else:
            send_message(sock=client, message={RESPONSE: 400, ERROR: "Bad request"})

    @staticmethod
    def process_message(message: dict, names: dict, send_lst: list):
        if message[DESTINATION] in names and names[message[DESTINATION]] in send_lst:
            send_message(sock=names[message[DESTINATION]], message=message)
            LOG.info(f"Client <{message[SENDER]}> send message to <{message[DESTINATION]}>")

        elif message[DESTINATION] in names and names[message[DESTINATION]] not in send_lst:
            raise ConnectionError

        else:
            LOG.info(f"User <{message[DESTINATION]}> offline")


def main() -> None:
    addr, port, _ = get_args()

    server_db.create_all()
    server_db.clear_active_users()

    server = Server(ip_address=addr, port=port)
    server.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        LOG.info("Server stopped")
