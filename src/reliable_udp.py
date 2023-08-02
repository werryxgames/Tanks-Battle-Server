"""Module, that guarantees receive of UDP packets."""
from json import dumps
from json import loads
from threading import Thread
from time import sleep

from singleton import get_data


class ReliableUDP:
    """Class, that guarantees receive of UDP packets."""

    def __init__(self, sock, addr):
        """Constructor of Reliable UDP."""
        self.sender_packet_id = 0
        self.sender_threads = {}
        self.received = []
        self.sock = sock
        self.addr = addr

        data = get_data()
        self.config = data[0]
        self.logger = data[1]

    @staticmethod
    def custom_sort(item):
        """Returns first element in list `item`."""
        return item[0]

    @staticmethod
    def spam_thread(sock, addr, message, packet_id, thr_array, config):
        """Sends packet to client, until gets ACK."""
        mesg = dumps([packet_id, message]).encode("utf8")
        thr_keys = thr_array.keys()
        timeout = config["udp_reliable_resend_timeout"]

        while packet_id in thr_keys:
            sock.sendto(mesg, addr)
            sleep(timeout)

    def send(self, message):
        """Sends Reliable UDP data to client."""
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
            f"Data, sent to client '{self.addr[0]}:{self.addr[1]}':",
            message
        )

    def send_unreliable(self, message):
        """Sends data of Unreliable UDP to client."""
        self.sock.sendto(dumps([-1, message]).encode("utf8"), self.addr)
        self.logger.slow(
            f"Data, sent to client '{self.addr[0]}:{self.addr[1]}':",
            message
        )

    def new_jdt(self, jdt, packet_id):
        """Called, when new packet is received."""
        matches = 0
        last_i = 0
        check = True

        self.received.append(jdt)
        self.received.sort(key=self.custom_sort)

        for i in self.received:
            if i[0] == packet_id:
                matches += 1

                if matches >= 2:
                    return None

            if check and i[0] == last_i:
                last_i += 1
            elif check:
                check = False

        last_i -= 1

        if packet_id <= last_i:
            return jdt[1]

        return None

    def receive(self, data):
        """Decodes and handles Reliable data of client."""
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

            if jdt not in self.received:
                return self.new_jdt(jdt, packet_id)

        except BaseException:
            self.logger.log_error_data()
            return False

        return None
