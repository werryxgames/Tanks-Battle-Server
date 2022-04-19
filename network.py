from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from client import Client
from json import loads, dumps
from threading import Thread
from accounts import AccountManager
from singleton import get_data


class NetworkedClient:
	def __init__(self, conn, addr):
		self.conn = conn
		self.addr = addr
		self.config, self.logger = get_data()
		self.client = Client(conn, addr)

	def send(self, message):
		self.conn.send(dumps(message).encode("utf8"))
		self.logger.debug(f"Отправлены данные клиенту '{self.addr[0]}:{self.addr[1]}':", message)

	def receive(self):
		success = False
		while True:
			try:
				self.logger.info(f"Клиент '{self.addr[0]}:{self.addr[1]}' подключён")
				data = self.conn.recv(1024)
				if not data:
					break
				jdt = loads(data.decode("utf8"))
				self.logger.debug(f"Получены данные от клиента '{self.addr[0]}:{self.addr[1]}':", jdt)
				try:
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
								success = self.client.set_login_data(args[0], args[1])
								break
							else:
								self.send(["register_fail", res])
					if com == "login":
						if args[2] not in self.config["accept_client_versions"]:
							self.send(["version_not_accepted"])
						else:
							self.client.version = args[2]
							res = AccountManager.login_account(args[0], args[1])
							if res == AccountManager.SUCCESSFUL:
								self.send(["login_successful", args[0], args[1]])
								success = self.client.set_login_data(args[0], args[1])
								break
							else:
								self.send(["login_fail", res])
				except IndexError:
					self.send(["something_wrong"])
					self.conn.close()
					break
			except ConnectionResetError:
				break
			except ConnectionAbortedError:
				break
		if success:
			self.logger.debug(f"Клиент '{self.addr[0]}:{self.addr[1]}' вошёл в аккаунт")
			self.client.receive()
		else:
			self.logger.info(f"Клиент '{self.addr[0]}:{self.addr[1]}' отключён")
			self.conn.close()


def start_tcp_server():
	config, logger = get_data()
	sock = socket(AF_INET, SOCK_STREAM)
	sock.bind((config["host"], config["port"]))
	sock.listen(config["clients_queue"])
	logger.info("TCP сервер запущен")
	logger.debug("Адрес:", config["host"] + ",", "порт:", config["port"])
	while True:
		conn, addr = sock.accept()
		nc = NetworkedClient(conn, addr)
		Thread(target=nc.receive, daemon=True).start()
	sock.close()
