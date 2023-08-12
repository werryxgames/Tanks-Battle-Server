"""Module for network sockets."""
from multiprocessing import Process
from multiprocessing import freeze_support
from os import getpid
from os import remove
from socket import AF_INET
from socket import SOCK_DGRAM
from socket import socket
from sys import platform

from absolute import to_absolute
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
    """Class of client."""

    CONSOLE = Console

    def __init__(self, sock_, addr):
        """Initialization of client."""
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
        """Closes connection with client."""
        try:
            self.send(ByteBuffer(2).put_16(2).to_bytes())
            clients.pop(self.addr)
            self.logger.info(
                f"Client '{self.addr[0]}:{self.addr[1]}' disconnected"
            )
        except OSError:
            pass

    def send(self, *args, **kwargs):
        """Sends Reliable UDP data to client."""
        self.rudp.send(*args, **kwargs)

    def handle_register(self, login, password):
        """Handles registration of client."""
        if not AccountManager.add_account_async(
            login,
            password,
            self
        ):
            clients.pop(self.addr)

    def handle_login(self, login, password):
        """Handles login of client into account."""
        if not AccountManager.login_account_async(
            login,
            password,
            self
        ):
            clients.pop(self.addr)

    def handle(self, code, data):
        """Handles data, received from client."""
        try:
            if code == 0:
                login = data.get_string()
                password = data.get_string()
                version = data.get_string()

                if version not in self.config["accept_client_versions"]:
                    self.send(ByteBuffer(2).put_u16(9).to_bytes())
                    return

                self.client.version = version
                self.handle_register(login, password)
                return

            if code == 1:
                login = data.get_string()
                password = data.get_string()
                version = data.get_string()

                if version not in self.config["accept_client_versions"]:
                    self.send(ByteBuffer(2).put_u16(9).to_bytes())
                    return

                self.client.version = version
                self.handle_login(login, password)
                return
        except BaseException:
            self.logger.log_error_data()
            self.close()
            return

    def receive(self, data):
        """Handles data from client."""
        rudp = self.rudp.receive(data)

        if rudp is False:
            self.close()
            return

        if rudp is None:
            return

        request_code = data.get_u16()

        if request_code == 7:
            clients.pop(self.addr)

        # Console is (temporary) unsupported
        if self.console is not None:
            data.seek(2)
            self.console.receive(data)
            return

        if self.send_client:
            self.client.receive(request_code, data)
            return

        self.handle(request_code, data)

    def check_is_first(self, data):
        """Checks is data correct for first receive()."""
        if self.send_client:
            return True

        if data.size() < 2:
            return False

        if data.get_u16() != 1:
            return False

        response = data.get_u16()
        data.rewind()
        return response < 2


def is_active():
    """Checks is server running."""
    return thr is not None


def stop_server():
    """Stops server."""
    global thr

    thr.terminate()

    data = get_data()
    gui = data[2]

    if gui is not None:
        if gui.state == gui.STATE_MAIN:
            gui.elements[2].configure(text="Status: stopped")
            gui.elements[3].configure(
                text="Start",
                command=start_server_async
            )

    thr = None
    remove(to_absolute("../run"))


def start_server_async():
    """Asynchronously starts server."""
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
                text=f"Status: started\tIP: {config['host']}"
            )
            gui.elements[3].configure(text="Stop", command=stop_server)


def on_new_client(logger, sock_, addr, data):
    """Function, that is called, when client connects."""
    if addr not in clients:
        clients[addr] = NetworkedClient(sock_, addr)

        if clients[addr].check_is_first(data):
            logger.info(f"Client '{addr[0]}:{addr[1]}' connected")
        else:
            del clients[addr]
            return True

    return False


def start_server(config, logger):
    """Synchronously starts server."""
    set_data(config, logger)

    sock_ = socket(AF_INET, SOCK_DGRAM)
    sock_.bind((config["host"], config["port"]))

    logger.info("Server started")
    logger.debug("Address:", config["host"] + ",", "port:", config["port"])

    with open(to_absolute("../run"), "wb") as file:
        pid = hex(getpid())[2:]
        file.write(bytes.fromhex(("0" if len(pid) % 2 else "") + pid))

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
                f"Client '{addr[0]}:{addr[1]}' sent data: {data.barr}"
            )
            data.rewind()
            clients[addr].receive(data)
        except ByteBufferException:
            clients[addr].sendto(ByteBuffer(4).put_16(1).put_16(2), addr)
            # Slow in case of DDoS
            logger.slow(
                f"Client '{addr[0]}:{addr[1]}' sent invalid data: \
'{data.barr}'"
            )

    sock_.close()


if platform.startswith("win"):
    freeze_support()
