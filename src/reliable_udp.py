"""Модуль гарантированной доставки UDP пакетов."""
from json import dumps
from json import loads
from threading import Thread
from time import sleep

from singleton import get_data


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
