"""Tanks Battle client."""
from copy import deepcopy

from accounts import AccountManager
from mjson import read
from netclasses import NetUser
from player import Player
from singleton import add_match
from singleton import get_clients
from singleton import get_const_params
from singleton import get_data
from singleton import get_matches

clients = get_clients()


class Client(NetUser):
    """Class for client in game."""

    def __init__(self, sock, addr, rudp):
        """Initialization of client."""
        self.sock = sock
        self.addr = addr
        self.config = get_data()[0]

        super().__init__(rudp)

        self.version = None
        self.player = None
        self.send_player = False

    def close(self):
        """Closes connection with client due to error."""
        try:
            self.send(["something_wrong"])
            clients.pop(self.addr)
            self.logger.info(
                f"Client '{self.account['nick']}' ('{self.addr[0]}:\
{self.addr[1]}') disconnected")
        except OSError:
            pass

    def redirect_player(self, data):
        """Redirects packet to Player, if possible."""
        if self.send_player:
            if self.player.receive(data) == Player.BACK_TO_MENU:
                self.send_player = False
                self.player = None

            return True
        return False

    def handle_account(self, com, _args):
        """Handles data of client's account."""
        if com == "get_account_data":
            self.refresh_account()
            self.send([
                "account_data",
                self.config["ranks"],
                self.account["xp"],
                self.account["crystals"],
                get_const_params()
            ])
            return True

        return False

    def update_client_data(self, fail_data):
        """Updates client data."""
        data = read("../data.json")

        if data is None:
            self.send(fail_data)
            return

        self.refresh_account()

        tanks = []

        for i, tank_ in enumerate(data["tanks"]):
            tanks.append({
                **tank_,
                "have": i in self.account["tanks"]
            })

        self.send([
            "garage_data",
            tanks,
            self.account["selected_tank"],
            self.account["crystals"]
        ])

    def select_tank(self, args):
        """Handles client's request to select args[0] from type_."""
        if args[0] in self.account["tanks"]:
            if AccountManager.set_account(
                self.account["nick"],
                "selected_tank",
                args[0]
            ) != AccountManager.SUCCESSFUL:
                self.send(["not_selected", 1])
                return

            self.update_client_data(["not_selected", 1])
            return

        self.send(["not_selected", 0])
        return

    def buy_tank_data(self, tank_id, data):
        """Handles purchase request with specified data."""
        if tank_id not in self.account["tanks"] and len(
            data["tanks"]
        ) > tank_id:
            tank = data["tanks"][tank_id]
            self.refresh_account()

            if self.account["crystals"] >= tank["price"]:
                if AccountManager.set_account(
                    self.account["nick"],
                    "crystals",
                    self.account["crystals"] - tank["price"]
                ) != AccountManager.SUCCESSFUL:
                    self.send(["not_selected", 1])
                    return

                if AccountManager.set_account(
                    self.account["nick"],
                    "tanks",
                    [*self.account["tanks"], tank_id]
                ) != AccountManager.SUCCESSFUL:
                    self.send(["not_selected", 1])
                    return

                if AccountManager.set_account(
                    self.account["nick"],
                    "selected_tank",
                    tank_id
                ) != AccountManager.SUCCESSFUL:
                    self.send(["not_selected", 1])
                    return

                self.update_client_data(["not_selected", 1])
                return

            self.send(["buy_failed", 0])
            return

        self.send(["not_selected", 0])

    def buy_tank(self, args):
        """Handles purchase request with data reading."""
        data = read("../data.json")

        if data is None:
            self.send(["not_selected", 2])
            return

        self.buy_tank_data(args[0], data)

    def handle_tanks(self, com, args):
        """Handles client's tanks."""
        if com == "select_tank":
            self.select_tank(args)
            return True

        if com == "buy_tank":
            self.buy_tank(args)
            return True

        return False

    def handle_garage(self, com, args):
        """Handles garade data of client."""
        if com == "get_garage_data":
            self.update_client_data(["garage_failed"])
            return True

        if self.handle_tanks(com, args):
            return True

        return False

    def handle_get_matches(self):
        """Handles matches get request from client."""
        matches = get_matches()
        res = deepcopy(matches)

        for match_ in res:
            match_["players"] = len(match_["players"])
            del match_["messages"]

        self.send(["matches", res])

    def handle_create_match(self, args):
        """Handles match creation from client."""
        self.refresh_account()

        if not isinstance(args[0], int):
            self.send(["game_create_failed", 1])
            return

        if not isinstance(args[1], str):
            self.send(["game_create_failed", 1])
            return

        map_id = args[0]

        if map_id < 0 or map_id >= len(read("../data.json")["maps"]):
            self.send(["game_create_failed", 1])
            return

        max_players = args[1].strip()

        if len(max_players) < 1:
            self.send(["game_create_failed", 2])
            return

        if not AccountManager.check(max_players, "0123456789"):
            self.send(["game_create_failed", 2])
            return

        max_players = int(max_players)

        if max_players < 1 or max_players > self.config["max_play\
ers_in_game"]:
            self.send(["game_create_failed", 0])
            return

        match_ = add_match(
            map_id,
            max_players
        )

        self.send(["game_created"])

        self.player = Player(
            self.sock,
            self.addr,
            match_,
            self.rudp
        )
        self.refresh_account()

        self.player.set_login_data(self.login, self.password)
        self.send_player = True

    def handle_join_battle(self, args):
        """Handles client join battle request."""
        matches = get_matches()
        player_match = None

        for match_id, match_ in enumerate(matches):
            if match_id == args[0]:
                if len(
                    match_["players"]
                ) < match_["max_players"]:
                    player_match = match_
                    self.send(["battle_joined"])

                    self.player = Player(
                        self.sock,
                        self.addr,
                        player_match,
                        self.rudp
                    )
                    self.refresh_account()

                    self.player.set_login_data(
                        self.login,
                        self.password
                    )
                    self.send_player = True
                    return

                self.send(["battle_not_joined", 1])
                return

        self.send(["battle_not_joined", 0])

    def handle_matches(self, com, args):
        """Handles matches."""
        if com == "get_matches":
            self.handle_get_matches()
            return True

        if com == "create_match":
            self.handle_create_match(args)
            return True

        if com == "join_battle":
            self.handle_join_battle(args)
            return True

        return False

    def handle_settings(self, com, args):
        """Handles client's settings."""
        if com == "request_settings":
            self.send(["settings", *self.account["settings"]])
            return True

        if com == "reset_settings":
            dsets = self.config["default_settings"]

            if AccountManager.set_account(
                self.account["nick"],
                "settings",
                dsets
            ) != AccountManager.SUCCESSFUL:
                self.send(["failed", 0])
                return True

            self.send(["settings", *dsets])
            return True

        if com == "apply_settings":
            try:
                if 99999 > int(args[2]) > 10:
                    nsets = args

                    if AccountManager.set_account(
                        self.account["nick"],
                        "settings",
                        nsets
                    ) != AccountManager.SUCCESSFUL:
                        self.send(["failed", 1])

                    return True

                self.send(["failed", 2])
            except ValueError:
                self.send(["failed", 3])

            return True

        return False

    def handle(self, code, data):
        """Hanldles packet of client."""
        if self.handle_account(code, data):
            return

        if self.handle_garage(code, data):
            return

        if self.handle_matches(code, data):
            return

        if self.handle_settings(code, data):
            return

    def receive(self, data):
        """Received client's packet."""
        if self.redirect_to_player(data):
            return

        try:
            code = data.get_u16()
            self.handle(code, data)
        except BaseException:
            self.logger.log_error_data()
            self.close()
            return
