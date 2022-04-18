from mjson import append, read

class AccountManager:
	SUCCESSFUL = 0
	FAILED_NICK_LENGTH = 1
	FAILED_UNKNOWN = 2
	FAILED_PASSWORD_LENGTH = 3
	FAILED_NICK_ALREADY_USED = 4
	FAILED_UNSAFE_CHARACTERS = 5
	FAILED_NOT_FOUND = 6
	FAILED_PASSWORD_NOT_MATCH = 7

	@staticmethod
	def check(string):
		return set(string.lower()) <= set("qwertyuiopasdfghjklzxcvbnm1234567890-=+*/[]:;.,\\|&%#@!$^()")

	@staticmethod
	def get_account(nick):
		data = read("data.json")
		if data is None:
			return AccountManager.FAILED_UNKNOWN
		for account in data["accounts"]:
			if account["nick"] == nick:
				return account
		return AccountManager.FAILED_NOT_FOUND

	@staticmethod
	def login_account(nick, password):
		if not isinstance(nick, str):
			return AccountManager.FAILED_UNKNOWN
		if not isinstance(password, str):
			return AccountManager.FAILED_UNKNOWN

		nick = nick.strip()
		password = password.strip()

		if len(nick) < 3 or len(nick) > 12:
			return AccountManager.FAILED_NICK_LENGTH
		if len(password) < 6 or len(password) > 16:
			return AccountManager.FAILED_PASSWORD_LENGTH

		if not AccountManager.check(nick):
			return AccountManager.FAILED_UNSAFE_CHARACTERS
		if not AccountManager.check(password):
			return AccountManager.FAILED_UNSAFE_CHARACTERS

		data = read("data.json")
		if data is None:
			return AccountManager.FAILED_UNKNOWN
		for account in data["accounts"]:
			if account["nick"] == nick:
				if account["password"] == password:
					return AccountManager.SUCCESSFUL
				else:
					return AccountManager.FAILED_PASSWORD_NOT_MATCH

		return AccountManager.FAILED_NOT_FOUND

	@staticmethod
	def add_account(nick, password):
		if not isinstance(nick, str):
			return AccountManager.FAILED_UNKNOWN
		if not isinstance(password, str):
			return AccountManager.FAILED_UNKNOWN

		nick = nick.strip()
		password = password.strip()

		if len(nick) < 3 or len(nick) > 12:
			return AccountManager.FAILED_NICK_LENGTH
		if len(password) < 6 or len(password) > 16:
			return AccountManager.FAILED_PASSWORD_LENGTH

		if not AccountManager.check(nick):
			return AccountManager.FAILED_UNSAFE_CHARACTERS
		if not AccountManager.check(password):
			return AccountManager.FAILED_UNSAFE_CHARACTERS

		data = read("data.json")
		if data is None:
			return AccountManager.FAILED_UNKNOWN
		for account in data["accounts"]:
			if account["nick"] == nick:
				return AccountManager.FAILED_NICK_ALREADY_USED

		acc = {
			"nick": nick,
			"password": password,
			"xp": 0,
			"tanks": {}
		}

		if append("data.json", "accounts", acc):
			return AccountManager.SUCCESSFUL
		return AccountManager.FAILED_UNKNOWN
