from json import loads, dumps
from accounts import AccountManager
from singleton import get_data
from mjson import read


class Player:
	def __init__(self, conn, addr, battle_data):
		self.conn = conn
		self.addr = addr
		self.bdata = battle_data
		self.config, self.logger = get_data()
		self.version = None
		self.login = None
		self.password = None
		self.account = None

	def set_login_data(self, login, password):
		self.login = login
		self.password = password
		self.account = AccountManager.get_account(login)

		if self.account == AccountManager.FAILED_UNKNOWN or self.account == AccountManager.FAILED_NOT_FOUND or self.account["password"] != password:
			return False

		return True

	def refresh_account(self):
		self.account = AccountManager.get_account(self.login)

		if self.account == AccountManager.FAILED_UNKNOWN or self.account == AccountManager.FAILED_NOT_FOUND or self.account["password"] != self.password:
			return False

		return True

	def send(self, message):
		self.conn.send(dumps(message).encode("utf8"))
		self.logger.debug(f"Отправлены данные клиенту '{self.addr[0]}:{self.addr[1]}':", message)

	def receive(self):
		while True:
			try:
				data = self.conn.recv(1024)

				if not data:
					break

				jdt = loads(data.decode("utf8"))
				self.logger.debug(f"Получены данные от клиента '{self.addr[0]}:{self.addr[1]}':", jdt)

				com = jdt[0]
				args = jdt[1:]

				if com == "get_battle_data":
					self.refresh_account()

					data = read("data.json")
					if data is None:
						self.send(["error_battle_data"])
						continue

					tank_data = data["tanks"][self.account["selected_tank"]]
					res_data = {}
					for k, v in tank_data.items():
						if k in ["durability", "mass", "speed", "gravity", "rotation_speed"]:
							res_data[k] = v

					self.send(["battle_data", self.bdata["map"], self.account["nick"], self.account["selected_tank"], res_data])

			except (ConnectionResetError, ConnectionAbortedError):
				self.logger.info(f"Клиент '{self.addr[0]}:{self.addr[1]}' отключён")
				self.conn.close()
				break

			except BaseException as e:
				self.logger.error(e)
				self.send(["something_wrong"])
				self.logger.info(f"Клиент '{self.addr[0]}:{self.addr[1]}' отключён")
				self.conn.close()
				break
