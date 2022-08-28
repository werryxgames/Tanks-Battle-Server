"""Модуль гарантированной доставки UDP пакетов."""
from json import dumps
from json import loads
from threading import Thread
from time import sleep

from singleton import get_data


class ByteTranslator:
    """Класс для преобразования байтов в данные и наоборот."""

    COM_BYTE_TRANSLATIONS = {
        "something_wrong": (0, 0),
        "register": (0, 1),
        "login": (0, 2),
        "get_account_data": (0, 3),
        "client_disconnected": (0, 4),
        "console_command": (0, 5)
    }

    @classmethod
    def get_com_bytes(cls, com):
        """Возвращает bytearray из com-строки."""
        try:
            return bytearray(cls.COM_BYTE_TRANSLATIONS[com])
        except KeyError:
            return bytearray(0, 0)

    @staticmethod
    def to_bytes(data):
        """Преобразует data в байты."""
        com = data[0]
        barr = ByteTranslator.get_com_bytes(com)

        for arg in data[1]:
            barr.append(type(arg))

            if isinstance(arg, str):
                for byte in arg.encode("utf8"):
                    barr.append(byte)

                barr.append(0)
            elif isinstance(arg, int):
                hexarg = hex(arg)[2:6]

                for byte in bytes.fromhex((4 - len(hexarg)) * "00" + hexarg):
                    barr.append(byte)

        return barr

    @staticmethod
    def to_data(bytes_):
        """Преобразует bytes_ в данные."""


class ReliableUDP:
    """Класс гарантированной доставки UDP пакетов."""

    def __init__(self, sock, addr):
        self.sender_packet_id = 0
        self.sender_threads = {}
        self.received = []
        self.sock = sock
        self.addr = addr

        data = get_data()
        self.config = data[0]
        self.logger = data[1]

    @staticmethod
    def spam_thread(sock, addr, message, packet_id, thr_array, config):
        """Отправляет пакеты клиенту, пока не получит ответ."""
        mesg = dumps([packet_id, message]).encode("utf8")
        thr_keys = thr_array.keys()
        timeout = config["udp_reliable_resend_timeout"]

        while packet_id in thr_keys:
            sock.sendto(mesg, addr)
            sleep(timeout)

    def send(self, message):
        """Отправляет Reliable UDP данные клиенту."""
        self.sender_threads[self.sender_packet_id] = Thread(
            target=self.spam_thread,
            args=(
                self.sock,
                self.addr,
                message,
                self.sender_packet_id,
                self.sender_threads,
                self.config
            )
        )
        self.sender_threads[self.sender_packet_id].start()
        self.sender_packet_id += 1
        self.logger.debug(
            f"Отправлены данные клиенту '{self.addr[0]}:{self.addr[1]}':",
            message
        )

    def send_unreliable(self, message):
        """Отправляет Unreliable UDP данные клиенту."""
        self.sock.sendto(dumps([-1, message]).encode("utf8"), self.addr)
        self.logger.slow(
            f"Отправлены данные клиенту '{self.addr[0]}:{self.addr[1]}':",
            message
        )

    def new_jdt(self, jdt, packet_id):
        """Вызывается при получении нового пакета."""
        if packet_id in self.received:
            return None

        max_packets = self.config["udp_reliable_max_packets"]

        for i in range(max(packet_id - max_packets, 0), packet_id):
            if i not in self.received:
                return None

        self.received.append(packet_id)

        if len(self.received) > max_packets:
            self.received = self.received[len(self.received) - max_packets:]

        return jdt[1]

    def receive(self, data):
        """Обрабатывает и декодирует Reliable данные клиента."""
        try:
            jdt = loads(data.decode("utf8"))

            packet_id = jdt[0]

            if packet_id == -1:
                return jdt[1]

            if packet_id == -2:
                arg = jdt[1]

                if arg in self.sender_threads:
                    thr = self.sender_threads[arg]
                    del self.sender_threads[arg]
                    thr.join()

                return None

            self.sock.sendto(dumps([-2, packet_id]).encode("utf8"), self.addr)

            return self.new_jdt(jdt, packet_id)

        except BaseException:
            self.logger.log_error_data()
            return False

        return None
