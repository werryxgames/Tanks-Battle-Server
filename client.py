from json import loads, dumps
from accounts import AccountManager
from singleton import get_data, get_matches, add_match, get_clients
from mjson import read
from player import Player
from copy import deepcopy

clients = get_clients()


class Client:
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.config, self.logger = get_data()
        self.version = None
        self.login = None
        self.password = None
        self.account = None
        self.send_player = False

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
        if self.send_player:
            self.player.receive(data)
        else:
            try:
                jdt = loads(data.decode("utf8"))

                com = jdt[0]
                args = jdt[1:]

                if com == "get_account_data":
                    self.refresh_account()
                    self.send(["account_data", self.account["xp"], self.account["crystals"]])

                elif com == "get_garage_data":
                    self.refresh_account()
                    tanks = []
                    guns = []
                    data = read("data.json")
                    if data is None:
                        self.send(["garage_failed"])
                        return
                    for i, tank in enumerate(data["tanks"]):
                        tanks.append({
                            **tank,
                            "have": i in self.account["tanks"]
                        })
                    for i, gun in enumerate(data["guns"]):
                        guns.append({
                            **gun,
                            "have": i in self.account["guns"]
                        })
                    self.send(["garage_data", tanks, self.account["selected_tank"], guns, self.account["selected_gun"]])

                elif com == "select_tank":
                    if args[0] in self.account["tanks"]:
                        if AccountManager.set_account(
                            self.account["nick"],
                            "selected_tank",
                            args[0]
                        ) != AccountManager.SUCCESSFUL:
                            self.send(["not_selected", 1])
                        else:
                            self.refresh_account()
                            tanks = []
                            guns = []
                            data = read("data.json")
                            if data is None:
                                self.send(["not_selected", 2])
                                return
                            for i, tank in enumerate(data["tanks"]):
                                tanks.append({
                                    **tank,
                                    "have": i in self.account["tanks"]
                                })
                            for i, gun in enumerate(data["guns"]):
                                guns.append({
                                    **gun,
                                    "have": i in self.account["guns"]
                                })
                            self.send(["garage_data", tanks, self.account["selected_tank"], guns, self.account["selected_gun"]])
                    else:
                        self.send(["not_selected", 0])

                elif com == "buy_tank":
                    data = read("data.json")
                    if data is None:
                        self.send(["not_selected", 2])
                        return
                    if args[0] not in self.account["tanks"] and len(data["tanks"]) > args[0]:
                        tank = data["tanks"][args[0]]
                        self.refresh_account()
                        if self.account["crystals"] >= tank["price"]:
                            if AccountManager.set_account(
                                self.account["nick"],
                                "crystals",
                                self.account["crystals"] - tank["price"]
                            ) != AccountManager.SUCCESSFUL:
                                self.send(["not_selected", 1])
                            elif AccountManager.set_account(
                                self.account["nick"],
                                "tanks",
                                [*self.account["tanks"], args[0]]
                            ) != AccountManager.SUCCESSFUL:
                                self.send(["not_selected", 1])
                            elif AccountManager.set_account(
                                self.account["nick"],
                                "selected_tank",
                                args[0]
                            ) != AccountManager.SUCCESSFUL:
                                self.send(["not_selected", 1])
                            else:
                                self.refresh_account()
                                tanks = []
                                guns = []
                                for i, tank_ in enumerate(data["tanks"]):
                                    tanks.append({
                                        **tank_,
                                        "have": i in self.account["tanks"]
                                    })
                                for i, gun in enumerate(data["guns"]):
                                    guns.append({
                                        **gun,
                                        "have": i in self.account["guns"]
                                    })
                                self.send(["garage_data", tanks, self.account["selected_tank"], guns, self.account["selected_gun"]])
                        else:
                            self.send(["buy_failed", 0])
                    else:
                        self.send(["not_selected", 0])

                elif com == "select_gun":
                    if args[0] in self.account["guns"]:
                        if AccountManager.set_account(
                            self.account["nick"],
                            "selected_gun",
                            args[0]
                        ) != AccountManager.SUCCESSFUL:
                            self.send(["not_selected", 1])
                        else:
                            self.refresh_account()
                            tanks = []
                            guns = []
                            data = read("data.json")
                            if data is None:
                                self.send(["not_selected", 2])
                                return
                            for i, tank in enumerate(data["tanks"]):
                                tanks.append({
                                    **tank,
                                    "have": i in self.account["tanks"]
                                })
                            for i, gun in enumerate(data["guns"]):
                                guns.append({
                                    **gun,
                                    "have": i in self.account["guns"]
                                })
                            self.send(["garage_data", tanks, self.account["selected_tank"], guns, self.account["selected_gun"]])
                    else:
                        self.send(["not_selected", 0])

                elif com == "buy_gun":
                    data = read("data.json")
                    if data is None:
                        self.send(["not_selected", 2])
                        return
                    if args[0] not in self.account["guns"] and len(data["guns"]) > args[0]:
                        gun = data["guns"][args[0]]
                        self.refresh_account()
                        if self.account["crystals"] >= gun["price"]:
                            if AccountManager.set_account(
                                self.account["nick"],
                                "crystals",
                                self.account["crystals"] - gun["price"]
                            ) != AccountManager.SUCCESSFUL:
                                self.send(["not_selected", 1])
                            elif AccountManager.set_account(
                                self.account["nick"],
                                "guns",
                                [*self.account["guns"], args[0]]
                            ) != AccountManager.SUCCESSFUL:
                                self.send(["not_selected", 1])
                            elif AccountManager.set_account(
                                self.account["nick"],
                                "selected_gun",
                                args[0]
                            ) != AccountManager.SUCCESSFUL:
                                self.send(["not_selected", 1])
                            else:
                                self.refresh_account()
                                tanks = []
                                guns = []
                                for i, tank in enumerate(data["tanks"]):
                                    tanks.append({
                                        **tank,
                                        "have": i in self.account["tanks"]
                                    })
                                for i, gun_ in enumerate(data["guns"]):
                                    guns.append({
                                        **gun_,
                                        "have": i in self.account["guns"]
                                    })
                                self.send(["garage_data", tanks, self.account["selected_tank"], guns, self.account["selected_gun"]])
                        else:
                            self.send(["buy_failed", 0])
                    else:
                        self.send(["not_selected", 0])

                elif com == "get_matches":
                    matches = get_matches()
                    res = deepcopy(matches)
                    for m in res:
                        m["players"] = len(m["players"])
                        del m["messages"]

                    self.send(["matches", res])

                elif com == "create_match":
                    self.refresh_account()

                    if not isinstance(args[0], str):
                        self.send(["game_create_failed", 1])
                        return
                    if not isinstance(args[1], str):
                        self.send(["game_create_failed", 1])
                        return

                    name = args[0].strip()
                    max_players = args[1].strip()

                    if len(name) < 3 or len(name) > 20:
                        self.send(["game_create_failed", 0])
                        return
                    if len(max_players) < 1 or len(max_players) > 2:
                        self.send(["game_create_failed", 0])
                        return

                    if not AccountManager.check(name, AccountManager.DEFAULT_ALLOWED + " "):
                        self.send(["game_create_failed", 3])
                        return
                    if not AccountManager.check(max_players, "0123456789"):
                        self.send(["game_create_failed", 3])
                        return

                    max_players = int(max_players)
                    if max_players < 1 or max_players > self.config["max_players_in_game"]:
                        self.send(["game_create_failed", 4])
                        return

                    matches = get_matches()
                    for match_ in matches:
                        if match_["name"] == name:
                            self.send(["game_create_failed", 2])
                            return

                    match_ = add_match(name, int(max_players), self.account["nick"])

                    self.send(["game_created"])

                    self.player = Player(self.sock, self.addr, match_)
                    self.refresh_account()

                    self.player.set_login_data(self.login, self.password)
                    self.send_player = True

                elif com == "join_battle":
                    matches = get_matches()
                    player_match = None

                    for match_ in matches:
                        if match_["name"] == args[0]:
                            if len(match_["players"]) < match_["max_players"]:
                                player_match = match_
                                self.send(["battle_joined"])

                                self.player = Player(self.sock, self.addr, player_match)
                                self.refresh_account()

                                self.player.set_login_data(self.login, self.password)
                                self.send_player = True

                                return
                            else:
                                self.send(["battle_not_joined", 1])

                                return

                    self.send(["battle_not_joined", 0])

            except BaseException as e:
                self.logger.error(e)
                self.close()
                if self.config["debug"]:
                    raise
                return
