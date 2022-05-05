from json import loads, dumps
from accounts import AccountManager
from singleton import get_data, get_clients
from mjson import read
from battle_player import BattlePlayer

clients = get_clients()


class Player:
    def __init__(self, sock, addr, battle_data):
        self.sock = sock
        self.addr = addr
        self.bdata = battle_data
        self.config, self.logger = get_data()
        self.version = None
        self.login = None
        self.password = None
        self.account = None
        self.bp = None

    def close(self):
        try:
            self.send(["something_wrong"])
            clients.pop(self.addr)
            self.logger.info(f"Клиент '{self.addr[0]}:{self.addr[1]}' отключён")
        except OSError:
            pass

    def set_login_data(self, login, password):
        self.login = login
        self.password = password
        self.account = AccountManager.get_account(login)

        if self.account == AccountManager.FAILED_UNKNOWN or \
        self.account == AccountManager.FAILED_NOT_FOUND or \
        self.account["password"] != password:
            return False

        return True

    def refresh_account(self):
        self.account = AccountManager.get_account(self.login)

        if self.account == AccountManager.FAILED_UNKNOWN or \
        self.account == AccountManager.FAILED_NOT_FOUND or \
        self.account["password"] != self.password:
            return False

        return True

    def send(self, message):
        self.sock.sendto(dumps(message).encode("utf8"), self.addr)
        self.logger.debug(f"Отправлены данные клиенту '{self.addr[0]}:{self.addr[1]}':", message)

    def receive(self, data):
        try:
            jdt = loads(data.decode("utf8"))

            com = jdt[0]
            args = jdt[1:]

            if com == "get_battle_data":
                self.refresh_account()

                self.bp = BattlePlayer(
                    self.account["nick"],
                    (0, 10, 0),
                    (0, 0, 0),
                    self.account["selected_tank"],
                    (0, 0, 0)
                )

                self.bdata["players"].append(self.bp)

                self.send([
                    "battle_data",
                    self.bdata["map"],
                    self.bp.json(),
                    self.bp.get_tank()
                ])

            if com == "request_tanks_data":
                self.bp.position = args[0]
                self.bp.rotation = args[1]

                players = self.bdata["players"]
                res = []
                for pl in players:
                    if pl is not self.bp:
                        res.append([pl.json(), pl.get_tank()])

                self.send(["tanks_data", res])

        except BaseException as e:
            self.logger.error(e)
            self.close()
            return
