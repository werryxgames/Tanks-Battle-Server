from json import dumps, loads
from threading import Thread
from singleton import get_data
from time import sleep


class ReliableUDP:
    def __init__(self, sock, addr):
        self.sender_packet_id = 0
        self.sender_threads = {}
        self.received = []
        self.sock = sock
        self.addr = addr
        self.config, self.logger = get_data()[:2]

    @staticmethod
    def custom_sort(item):
        return item[0]

    @staticmethod
    def spam_thread(sock, addr, message, packet_id, thr_array, config):
        mesg = dumps([packet_id, message]).encode("utf8")
        thr_keys = thr_array.keys()
        timeout = config["udp_reliable_resend_timeout"]

        while packet_id in thr_keys:
            sock.sendto(mesg, addr)
            sleep(timeout)

    def send(self, message):
        self.sender_threads[self.sender_packet_id] = Thread(target=self.spam_thread, args=(self.sock, self.addr, message, self.sender_packet_id, self.sender_threads, self.config))
        self.sender_threads[self.sender_packet_id].start()
        self.sender_packet_id += 1
        self.logger.debug(f"Отправлены данные клиенту '{self.addr[0]}:{self.addr[1]}':", message)

    def send_unreliable(self, message):
        self.sock.sendto(dumps([-1, message]).encode("utf8"), self.addr)
        self.logger.debug(f"Отправлены данные клиенту '{self.addr[0]}:{self.addr[1]}':", message)

    def receive(self, data):
        try:
            jdt = loads(data.decode("utf8"))

            packet_id = jdt[0]

            if packet_id == -1:
                return jdt[1]

            if packet_id == -2:
                arg = jdt[1]

                if arg in self.sender_threads.keys():
                    thr = self.sender_threads[arg]
                    del self.sender_threads[arg]
                    thr.join()

                return

            self.sock.sendto(dumps([-2, packet_id]).encode("utf8"), self.addr)

            matches = 0
            last_i = 0
            check = True

            if jdt not in self.received:
                self.received.append(jdt)
                self.received.sort(key=self.custom_sort)

                for i in self.received:
                    if i[0] == packet_id:
                        matches += 1

                        if matches >= 2:
                            return
                    if check and i[0] == last_i:
                        last_i += 1
                    elif check:
                        check = False

                last_i -= 1

                if packet_id <= last_i:
                    return jdt[1]

        except:
            self.logger.log_error_data()

            return False
