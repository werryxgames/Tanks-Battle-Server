"""Модуль управления сетью."""
from json import dumps
from multiprocessing import Process
from multiprocessing import freeze_support
from socket import AF_INET
from socket import SOCK_DGRAM
from socket import socket
from sys import platform

from accounts import AccountManager
from client import Client
from console import Console
from reliable_udp import ReliableUDP
from singleton import get_clients
from singleton import get_data
from singleton import set_data
from serializer import ByteBuffer
from serializer import ByteBufferException

thr = None
sock = None
clients = get_clients()


class NetworkedClient:
    """Класс клиента."""

    CONSOLE = Console

    def __init__(self, sock_, addr):
        """Инициализация клиента."""
        self.sock = sock_
        self.addr = addr
        self.rudp = ReliableUDP(sock_, addr)

        data = get_data()
        self.config = data[0]
        self.logger = data[1]

        self.client = Client(sock, addr, self.rudp)
        self.send_client = False
        self.console = None

    def close(self):
        """Закрывает соединение с клиентом."""
        try:
            self.send(["something_wrong"])
            clients.pop(self.addr)
            self.logger.info(
                f"Клиент '{self.addr[0]}:{self.addr[1]}' отключён"
            )
        except OSError:
            pass

    def send(self, *args, **kwargs):
        """Отправляет Reliable UDP данные клиенту."""
        self.rudp.send(*args, **kwargs)

    def handle_register(self, login, password):
        """Обрабатывает рагистрацию клиента."""
        if not AccountManager.add_account_async(
            login,
            password,
            self
        ):
            self.send(["already_queued"])
            clients.pop(self.addr)

    def handle_login(self, login, password):
        """Обрабатывает вход клиента в аккаунт."""
        if not AccountManager.login_account_async(
            login,
            password,
            self
        ):
            self.send(["already_queued"])
            clients.pop(self.addr)

    def handle(self, code, data):
        """Обрабатывает данные от клиента."""
        try:
            if code == 0:
                login = data.get_string()
                password = data.get_string()
                version = data.get_string()

                if version not in self.config["accept_client_versions"]:
                    self.send(10000)
                    return

                self.client.version = version
                self.handle_register(login, password)
                return

            if code == 1:
                login = data.get_string()
                password = data.get_string()
                version = data.get_string()

                if version not in self.config["accept_client_versions"]:
                    self.send(10000)
                    return

                self.client.version = version
                self.handle_login(login, password)
                return

        except BaseException:
            self.logger.log_error_data()
            self.close()
            return

    def receive(self, data):
        """Обрабатывает данные от клиента."""
        rudp = self.rudp.receive(data)

        if rudp is False:
            self.close()
            return

        if rudp is None:
            return

        request_code = data.get_u16()

        if request_code in [7, 11]:
            clients.pop(self.addr)

            if request_code == "client_disconnected":
                return

        # Console is (temporary) unsupported
        if self.console is not None:
            data.seek(2)
            self.console.receive(data)
            return

        if self.send_client:
            data.seek(2)
            self.client.receive(data)
            return

        self.handle(request_code, data)

    def check_is_first(self, pdata):
        """Проверяет является ли pdata нормальной для первого receive()."""
        if self.send_client:
            return True

        if data.get_u16() < 2:
            return False

        response = data.get_u16() < 2
        data.rewind()
        return response


def is_active():
    """Проверяет запущен ли сервер."""
    return thr is not None


def stop_server():
    """Останавливает сервер."""
    global thr

    thr.terminate()

    data = get_data()
    gui = data[2]

    if gui is not None:
        if gui.state == gui.STATE_MAIN:
            gui.elements[2].configure(text="Статус: не запущен")
            gui.elements[3].configure(
                text="Запустить",
                command=start_server_async
            )

    thr = None


def start_server_async():
    """Асинхронно запускает сервер."""
    global thr

    data = get_data()
    config = data[0]
    logger = data[1]
    gui = data[2]

    thr = Process(target=start_server, args=(config, logger))
    thr.start()

    if gui is not None:
        if gui.state == gui.STATE_MAIN:
            gui.elements[2].configure(
                text=f"Статус: запущен\tIP: {config['host']}"
            )
            gui.elements[3].configure(text="Остановить", command=stop_server)


def on_new_client(logger, sock_, addr, data):
    """Функция, вызываемая при подключении клиента."""
    if addr not in clients:
        clients[addr] = NetworkedClient(sock_, addr)

        if clients[addr].check_is_first(data):
            logger.info(f"Клиент '{addr[0]}:{addr[1]}' подключён")
        else:
            del clients[addr]
            return True

    return False


def start_server(config, logger):
    """Синхронно запускает сервер."""
    set_data(config, logger)

    sock_ = socket(AF_INET, SOCK_DGRAM)
    sock_.bind((config["host"], config["port"]))

    logger.info("Сервер запущен")
    logger.debug("Адрес:", config["host"] + ",", "порт:", config["port"])

    while True:
        try:
            adrdata = sock_.recvfrom(1024)
        except (ConnectionResetError, ConnectionAbortedError):
            continue

        data = ByteBuffer(adrdata[0])
        addr = adrdata[1]

        if on_new_client(logger, sock_, addr, data):
            continue

        try:
            func = [logger.debug, logger.slow][int(data.get_u16() < 2)]
            func(
                f"Клиент '{addr[0]}:{addr[1]}' отправил данные: '{data.get_fully()}'"
            )
            data.rewind()
            clients[addr].receive(data)
        except ByteBufferException():
            clients[addr].sendto(ByteBuffer(4).put_16(1).put_16(10000), addr)
            logger.warning(
                f"Клиент '{addr[0]}:{addr[1]}' отправил неверные данные: \
'{data.barr}'"
            )

    sock_.close()


if platform.startswith("win"):
    freeze_support()
