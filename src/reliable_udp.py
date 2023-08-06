"""Module, that guarantees receive of UDP packets."""
from json import dumps
from threading import Thread
from time import sleep

from singleton import get_data
from serializer import ByteBuffer


class ReliableUDP:
    """Class, that guarantees receive of UDP packets."""

    def __init__(self, sock, addr):
        """Constructor of Reliable UDP."""
        self.sender_packet_id = 2
        self.sender_threads = {}
        self.received = []
        self.sock = sock
        self.addr = addr

        data = get_data()
        self.config = data[0]
        self.logger = data[1]

    @staticmethod
    def spam_thread(sock, addr, message, packet_id, thr_array, config):
        """Sends packet to client, until gets ACK."""
        mesg = (
            ByteBuffer(2 + len(message))
            .put_u16(packet_id)
            .put_bytes(message)
            .to_bytes()
        )
        thr_keys = thr_array.keys()
        timeout = config["udp_reliable_resend_timeout"]

        while packet_id in thr_keys:
            sock.sendto(mesg, addr)
            sleep(timeout)

    def send(self, message):
        """Sends Reliable UDP data to client."""
        if not isinstance(message, (bytes, bytearray)):
            raise ValueError("Message should be bytes or bytearray")

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
        buffer: ByteBuffer = ByteBuffer(2 + len(message))
        buffer.put_u16(1)
        buffer.put_bytes(message)
        self.sock.sendto(buffer.to_bytes(), self.addr)
        self.logger.slow(
            f"Data, sent to client '{self.addr[0]}:{self.addr[1]}':",
            message
        )

    def new_jdt(self, packet_id):
        """Called, when new packet is received."""
        if packet_id in self.received:
            return None

        max_packets = self.config["udp_reliable_max_packets"]

        for i in range(max(packet_id - max_packets, 2), packet_id):
            if i not in self.received:
                return None

        self.received.append(packet_id)

        if len(self.received) > max_packets:
            self.received = self.received[len(self.received) - max_packets:]

        return True

    def receive(self, data):
        """Decodes and handles Reliable data of client."""
        try:
            packet_id = data.get_u16()

            # Unreliable packet
            if packet_id == 1:
                return True

            # ACK packet
            if packet_id == 0:
                arg = data.get_u16()

                if arg in self.sender_threads:
                    thr = self.sender_threads[arg]
                    del self.sender_threads[arg]
                    thr.join()

                return None

            self.sock.sendto(
                ByteBuffer(2 + 2).put_u16(0).put_u16(packet_id).to_bytes(),
                self.addr
            )
            return self.new_jdt(packet_id)
        except BaseException:
            self.logger.log_error_data()
            return False
