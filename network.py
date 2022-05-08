from json import loads, dumps, JSONDecodeError
from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM
from client import Client
from console import Console
from accounts import AccountManager
from singleton import get_data, get_clients

clients = get_clients()


class NetworkedClient:
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.config, self.logger = get_data()
        self.client = Client(sock, addr)
        self.send_client = False
        self.console = None

    def close(self):
        try:
            self.send(["something_wrong"])
            clients.pop(self.addr)
            self.logger.info(f"Клиент '{self.addr[0]}:{self.addr[1]}' отключён")
        except OSError:
            pass

    def send(self, message):
        self.sock.sendto(dumps(message).encode("utf8"), self.addr)
        self.logger.debug(f"Отправлены данные клиенту '{self.addr[0]}:{self.addr[1]}':", message)

    def receive(self, data):
        if self.console is not None:
            self.console.receive(data)
        elif self.send_client:
            self.client.receive(data)
        else:
            try:
                jdt = loads(data.decode("utf8"))

                com = jdt[0]
                args = jdt[1:]

                if com == "register":
                    if args[2] not in self.config["accept_client_versions"]:
                        self.send(["version_not_accepted"])
                    else:
                        self.client.version = args[2]

                        res = AccountManager.add_account(args[0], args[1])

                        if res == AccountManager.SUCCESSFUL:
                            self.send(["register_successful", args[0], args[1]])
                            self.client.set_login_data(args[0], args[1])
                            self.send_client = True
                            return
                        self.send(["register_fail", res])

                elif com == "login":
                    if args[2] not in self.config["accept_client_versions"]:
                        self.send(["version_not_accepted"])
                    else:
                        self.client.version = args[2]

                        res = AccountManager.login_account(args[0], args[1])

                        if res == AccountManager.SUCCESSFUL:
                            self.send(["login_successful", args[0], args[1]])
                            self.client.set_login_data(args[0], args[1])
                            self.send_client = True
                            return
                        if res == AccountManager.FAILED_CONSOLE:
                            self.send(["login_fail", res, args[0], args[1]])
                            self.console = Console(self.sock, self.addr)
                            return
                        if isinstance(res, list):
                            if res[0] == AccountManager.FAILED_BAN:
                                self.send(["login_fail", *res])
                                return
                        self.send(["login_fail", res])

            except BaseException as e:
                self.logger.error(e)
                self.close()
                if self.config["debug"]:
                    raise
                return


def start_server():
    config, logger = get_data()

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((config["host"], config["port"]))

    logger.info("Сервер запущен")
    logger.debug("Адрес:", config["host"] + ",", "порт:", config["port"])

    while True:
        try:
            adrdata = sock.recvfrom(1024)
        except (ConnectionResetError, ConnectionAbortedError):
            logger.debug(f"Клиент отключён")
        data = adrdata[0]
        addr = adrdata[1]
        if addr not in clients.keys():
            clients[addr] = NetworkedClient(sock, addr)
            logger.info(f"Клиент '{addr[0]}:{addr[1]}' подключён")
        try:
            tdata = loads(data.decode('utf8'))
            logger.debug(f"Клиент '{addr[0]}:{addr[1]}' отправил данные: '{tdata}'")
            clients[addr].receive(data)
        except JSONDecodeError:
            try:
                tdata = data.decode('utf8')
                logger.warning(f"Клиент '{addr[0]}:{addr[1]}' отправил не JSON данные: '{tdata}'")
            except UnicodeDecodeError:
                tdata = data
                logger.warning(f"Клиент '{addr[0]}:{addr[1]}' отправил не UTF-8 данные: '{tdata}'")

    sock.close()
