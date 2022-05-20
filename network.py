from json import loads, dumps, JSONDecodeError
from sys import platform
from multiprocessing import Process, freeze_support
from socket import socket, AF_INET, SOCK_DGRAM
from client import Client
from console import Console
from accounts import AccountManager
from singleton import get_data, get_clients, set_data
from reliable_udp import ReliableUDP

thr = None
sock = None
clients = get_clients()


class NetworkedClient:
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.rudp = ReliableUDP(sock, addr)
        self.config, self.logger = get_data()[:2]
        self.client = Client(sock, addr, self.rudp)
        self.send_client = False
        self.console = None

    def close(self):
        try:
            self.send(["something_wrong"])
            clients.pop(self.addr)
            self.logger.info(f"Клиент '{self.addr[0]}:{self.addr[1]}' отключён")
        except OSError:
            pass

    def send(self, *args, **kwargs):
        self.rudp.send(*args, **kwargs)

    def receive(self, data):
        rudp = self.rudp.receive(data)

        if rudp is False:
            self.close()

            return

        if rudp is None:
            return

        pdata = rudp

        if self.console is not None:
            self.console.receive(pdata)
        elif self.send_client:
            self.client.receive(pdata)
        else:
            try:
                com = pdata[0]
                args = pdata[1:]

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
                            self.console = Console(self.sock, self.addr, self.rudp)

                            return

                        if isinstance(res, list):
                            if res[0] == AccountManager.FAILED_BAN:
                                self.send(["login_fail", *res])

                                return

                        self.send(["login_fail", res])

            except:
                self.logger.log_error_data()
                self.close()

                return


def is_active():
    return thr is not None


def stop_server():
    global sock, thr

    thr.terminate()

    _config, _logger, gui = get_data()

    if gui is not None:
        if gui.state == gui.STATE_MAIN:
            gui.elements[2].configure(text="Статус: не запущен")
            gui.elements[3].configure(text="Запустить", command=start_server_async)

    thr = None


def start_server_async():
    global thr

    config, logger, gui = get_data()

    thr = Process(target=start_server, args=(config, logger))
    thr.start()

    if gui is not None:
        if gui.state == gui.STATE_MAIN:
            gui.elements[2].configure(text=f"Статус: запущен\tIP: {config['host']}")
            gui.elements[3].configure(text="Остановить", command=stop_server)


def start_server(config, logger):
    set_data(config, logger)

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
            func = [logger.debug, logger.slow][int(tdata[0] == -1)]
            func(f"Клиент '{addr[0]}:{addr[1]}' отправил данные: '{tdata[1]}'")
            clients[addr].receive(data)
        except JSONDecodeError:
            try:
                tdata = data.decode('utf8')
                logger.warning(f"Клиент '{addr[0]}:{addr[1]}' отправил не JSON данные: '{tdata}'")
            except UnicodeDecodeError:
                tdata = data
                logger.warning(f"Клиент '{addr[0]}:{addr[1]}' отправил не UTF-8 данные: '{tdata}'")
        except IndexError:
            tdata = data
            logger.warning(f"Клиент '{addr[0]}:{addr[1]}' отправил неверные данные: '{tdata}'")

    sock.close()


if platform.startswith("win"):
    freeze_support()
