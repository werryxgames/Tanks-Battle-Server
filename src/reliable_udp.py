"""Модуль гарантированной доставки UDP пакетов."""
from json import dumps
from json import loads
from struct import pack
from threading import Thread
from time import sleep

from singleton import get_data


class ByteTranslatorException(Exception):
    """Базовое исключение для ByteTranslator."""


class ByteTranslator:
    """Класс для преобразования байтов в данные и наоборот."""

    COM_BYTE_TRANSLATIONS = {
        "something_wrong": (0, 1),
        "register": (0, 2),
        "login": (0, 3),
        "get_account_data": (0, 4),
        "client_disconnected": (0, 5),
        "console_command": (0, 6)
    }
    DATATYPES = {
        int: 1,
        str: 2,
        float: 3,
        list: 4,
        tuple: 4,
        dict: 5,
        type(None): 6,
        bool: 7
    }

    @classmethod
    def get_com_bytes(cls, com):
        """Возвращает bytearray из com-строки."""
        try:
            return bytearray(cls.COM_BYTE_TRANSLATIONS[com])
        except KeyError:
            pass

        raise ByteTranslatorException("Указанная com-строка не найдена")

    @classmethod
    def get_datatype(cls, data):
        """Возвращает тип данных как число."""
        try:
            return cls.DATATYPES[type(data)]
        except KeyError:
            pass

        raise ByteTranslatorException("Тип указанных данных не найден")

    @staticmethod
    def bappend(original_barr, appending_barr):
        """Добавляет appending_barr к original_barr."""
        for byte in appending_barr:
            original_barr.append(byte)

    @staticmethod
    def str_to_bytes(data):
        """Преобразует строку в байты."""
        barr = bytearray()

        for byte in data.encode("utf8"):
            barr.append(byte)

        barr.append(0)
        return barr

    @staticmethod
    def int_to_bytes(data):
        """Преобразует целое число в байты."""
        barr = bytearray()
        last_length = -1

        for length in range(1, 257):
            try:
                bytes_ = int.to_bytes(data, length, "big", signed=True)
                last_length = length - 1
                break
            except OverflowError:
                continue

        barr.append(last_length)
        ByteTranslator.bappend(barr, bytes_)
        return barr

    @staticmethod
    def float_to_bytes(data):
        """Преобразует дробное число в байты."""
        barr = bytearray()
        ByteTranslator.bappend(barr, pack("f", data))
        return barr

    @staticmethod
    def array_to_bytes(data):
        """Преобразует массив в байты."""
        barr = bytearray()

        try:
            barr.append(len(data))
            ByteTranslator.bappend(barr, ByteTranslator.to_bytes(data))
            return barr
        except ValueError:
            pass

        raise ByteTranslatorException("Длина массива больше максимальной")

    @staticmethod
    def dict_to_bytes(data):
        """Преобразует словарь в байты."""
        barr = bytearray()
        dictval = []

        for key, value in data.items():
            dictval.append((key, value))

        try:
            barr.append(len(dictval))

            for byte in ByteTranslator.to_bytes(dictval):
                barr.append(byte)

            return barr
        except ValueError:
            pass

        raise ByteTranslatorException("Длина словаря больше максимальной")

    @staticmethod
    def bool_to_bytes(data):
        """Преобразует булевое значение в байты."""
        return bytearray([1]) if data else bytearray([0])

    @staticmethod
    def to_bytes(data):
        """Преобразует data в байты."""
        barr = bytearray()

        for arg in data:
            dtype = ByteTranslator.get_datatype(arg)
            barr.append(dtype)

            if dtype == 1:
                ByteTranslator.bappend(
                    barr,
                    ByteTranslator.int_to_bytes(arg)
                )
            elif dtype == 2:
                ByteTranslator.bappend(
                    barr,
                    ByteTranslator.str_to_bytes(arg)
                )
            elif dtype == 3:
                ByteTranslator.bappend(
                    barr,
                    ByteTranslator.float_to_bytes(arg)
                )
            elif dtype == 4:
                ByteTranslator.bappend(
                    barr,
                    ByteTranslator.array_to_bytes(arg)
                )
            elif dtype == 5:
                ByteTranslator.bappend(
                    barr,
                    ByteTranslator.dict_to_bytes(arg)
                )
            elif dtype == 7:
                barr.append(1 if arg else 0)

        return barr

    @staticmethod
    def to_data(bytes_):
        """Преобразует bytes_ в данные."""


class ReliableUDP:
    """Класс гарантированной доставки UDP пакетов."""

    def __init__(self, sock, addr):
        """Инициализация Reliable UDP."""
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
