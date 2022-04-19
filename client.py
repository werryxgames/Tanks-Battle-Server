from accounts import AccountManager
from json import loads, dumps
from singleton import get_data


class Client:
	def __init__(self, conn, addr):
		self.conn = conn
		self.addr = addr
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
				try:
					com = jdt[0]
					args = jdt[1:]
					if com == "get_account_data":
						self.refresh_account()
						self.send(["account_data", self.account["xp"]])
					elif com == "get_garage_data":
						self.refresh_account()
						tanks = []
						data = read("data.json")
						if data is None:
							self.send(["garage_failed"])
							continue
						for i, tank in enumerate(self.data["tanks"]):
							tanks.append({
								"have": i in self.account["tanks"],
								"name": tank["name"],
								"description": tank["description"],
								"price": tank["price"]
							})
						self.send(["garage_data", tanks])
				except IndexError:
					self.send(["something_wrong"])
			except ConnectionResetError:
				break
