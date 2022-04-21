from json import loads, dumps
from accounts import AccountManager
from singleton import get_data, get_matches, add_match, remove_match
from mjson import read


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
						self.send(["account_data", self.account["xp"], self.account["crystals"]])

					elif com == "get_garage_data":
						self.refresh_account()
						tanks = []
						data = read("data.json")
						if data is None:
							self.send(["garage_failed"])
							continue
						for i, tank in enumerate(data["tanks"]):
							tanks.append({
								**tank,
								"have": i in self.account["tanks"]
							})
						self.send(["garage_data", tanks, self.account["selected_tank"]])

					elif com == "select_tank":
						if args[0] in self.account["tanks"]:
							if AccountManager.set_account(self.account["nick"], "selected_tank", args[0]) != AccountManager.SUCCESSFUL:
								self.send(["not_selected", 1])
							else:
								self.refresh_account()
								tanks = []
								data = read("data.json")
								if data is None:
									self.send(["not_selected", 2])
									continue
								for i, tank in enumerate(data["tanks"]):
									tanks.append({
										**tank,
										"have": i in self.account["tanks"]
									})
								self.send(["garage_data", tanks, self.account["selected_tank"]])
						else:
							self.send(["not_selected", 0])

					elif com == "buy_tank":
						data = read("data.json")
						if data is None:
							self.send(["not_selected", 2])
							continue
						if args[0] not in self.account["tanks"] and len(data["tanks"]) > args[0]:
							tank = data["tanks"][args[0]]
							self.refresh_account()
							if self.account["crystals"] >= tank["price"]:
								if AccountManager.set_account(self.account["nick"], "crystals", self.account["crystals"] - tank["price"]) != AccountManager.SUCCESSFUL:
									self.send(["not_selected", 1])
								elif AccountManager.set_account(self.account["nick"], "tanks", [*self.account["tanks"], args[0]]) != AccountManager.SUCCESSFUL:
									self.send(["not_selected", 1])
								elif AccountManager.set_account(self.account["nick"], "selected_tank", args[0]) != AccountManager.SUCCESSFUL:
									self.send(["not_selected", 1])
								else:
									self.refresh_account()
									tanks = []
									for i, tank_ in enumerate(data["tanks"]):
										tanks.append({
											**tank_,
											"have": i in self.account["tanks"]
										})
									self.send(["garage_data", tanks, self.account["selected_tank"]])
							else:
								self.send(["buy_failed", 0])
						else:
							self.send(["not_selected", 0])

					elif com == "get_matches":
						matches = get_matches()
						result = []
						for match_ in matches:
							if match_["players"] < match_["max_players"]:
								result.append(match_)

						self.send(["matches", result])

					elif com == "create_match":
						self.refresh_account()

						if not isinstance(args[0], str):
							self.send(["game_create_failed", 1])
							continue
						if not isinstance(args[1], str):
							self.send(["game_create_failed", 1])
							continue

						name = args[0].strip()
						max_players = args[1].strip()

						if len(name) < 3 or len(name) > 20:
							self.send(["game_create_failed", 0])
							continue
						if len(max_players) < 1 or len(max_players) > 2:
							self.send(["game_create_failed", 0])
							continue

						if not AccountManager.check(name, AccountManager.DEFAULT_ALLOWED + " "):
							self.send(["game_create_failed", 3])
							continue
						if not AccountManager.check(max_players, "0123456789"):
							self.send(["game_create_failed", 3])
							continue

						max_players = int(max_players)
						if max_players < 1 or max_players > self.config["max_players_in_game"]:
							self.send(["game_create_failed", 4])
							continue

						matches = get_matches()
						exit = False
						for match_ in matches:
							if match_["name"] == name:
								self.send(["game_create_failed", 2])
								exit = True
								break
						if exit:
							continue

						match = add_match(name, int(max_players), self.account["nick"])

						self.send(["game_created"])

					elif com == "join_battle":
						matches = get_matches()
						exit = False
						for match_ in matches:
							if match_["name"] == args[0]:
								match_["players"] += 1
								self.send(["battle_joined"])
								if match_["players"] >= match_["max_players"]:
									remove_match(args[0])
								exit = True
								break
						if exit:
							continue
						self.send(["battle_not_joined", 0])

				except IndexError:
					self.send(["something_wrong"])
					self.conn.close()
					break

			except (ConnectionResetError, ConnectionAbortedError):
				break
