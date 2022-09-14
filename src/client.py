"""Клиент Tanks Battle."""
from copy import deepcopy

from accounts import AccountManager
from mjson import read
from netclasses import NetUser
from player import Player
from singleton import add_match
from singleton import get_clients
from singleton import get_matches

clients = get_clients()


class Client(NetUser):
    """Класс клиента в игре."""

    def __init__(self, sock, addr, rudp):
        """Инициализация клиента."""
        self.sock = sock
        self.addr = addr

        super().__init__(rudp)

        self.version = None
        self.player = None
        self.send_player = False

    def close(self):
        """Закрывает соединение с клиентом из-за ошибки."""
        try:
            self.send(["something_wrong"])
            clients.pop(self.addr)
            self.logger.info(
                f"Клиент '{self.account['nick']}' ('{self.addr[0]}:\
{self.addr[1]}') отключён")
        except OSError:
            pass

    def redirect_player(self, jdt):
        """Перенаправляет пакет на Player, если возможно."""
        if self.send_player:
            if self.player.receive(jdt) == Player.BACK_TO_MENU:
                self.send_player = False
                self.player = None

            return True

        return False

    def handle_account(self, com, _args):
        """Обрабатывает данные аккаунта клиента."""
        if com == "get_account_data":
            self.refresh_account()
            self.send([
                "account_data",
                self.account["xp"],
                self.account["crystals"]
            ])
            return True

        return False

    def update_client_data(self, fail_data):
        """Обновляет данные клиента."""
        data = read("data.json")

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
        """Обрабатывает запрос клиента на выбор args[0] из type_."""
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
        """Обрабатывает запрос на покупку танка с указанными данными."""
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
        """Обрабатывает запрос на покупку танка с чтением данных."""
        data = read("data.json")

        if data is None:
            self.send(["not_selected", 2])
            return

        self.buy_tank_data(args[0], data)

    def handle_tanks(self, com, args):
        """Обрабатывает танки клиента."""
        if com == "select_tank":
            self.select_tank(args)
            return True

        if com == "buy_tank":
            self.buy_tank(args)
            return True

        return False

    def handle_garage(self, com, args):
        """Обрабатывает данные гаража клиента."""
        if com == "get_garage_data":
            self.update_client_data(["garage_failed"])
            return True

        if self.handle_tanks(com, args):
            return True

        return False

    def handle_get_matches(self):
        """Обрабатывает получение матчей от клиента."""
        matches = get_matches()
        res = deepcopy(matches)

        for match_ in res:
            match_["players"] = len(match_["players"])
            del match_["messages"]

        self.send(["matches", res])

    def handle_create_match(self, args):
        """Обрабатывает создание матча от клиента."""
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

        if not AccountManager.check(
            name,
            AccountManager.DEFAULT_ALLOWED + " "
        ):
            self.send(["game_create_failed", 3])
            return

        if not AccountManager.check(max_players, "0123456789"):
            self.send(["game_create_failed", 3])
            return

        max_players = int(max_players)

        if max_players < 1 or max_players > self.config["max_play\
ers_in_game"]:
            self.send(["game_create_failed", 4])
            return

        matches = get_matches()

        for match_ in matches:
            if match_["name"] == name:
                self.send(["game_create_failed", 2])
                return

        match_ = add_match(
            name,
            int(max_players),
            self.account["nick"]
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
        """Обрабатывает присоединение клиента к матчу."""
        matches = get_matches()
        player_match = None

        for match_ in matches:
            if match_["name"] == args[0]:
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
        """Обрабатывает матчи."""
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
        """Обрабатывает настройки клиента."""
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

    def handle(self, com, args):
        """Обрабатывает пакет клиента."""
        if self.handle_account(com, args):
            return

        if self.handle_garage(com, args):
            return

        if self.handle_matches(com, args):
            return

        if self.handle_settings(com, args):
            return

    def receive(self, jdt):
        """Получает пакет клиента."""
        if self.redirect_player(jdt):
            return

        try:
            com = jdt[0]
            args = jdt[1:]

            self.handle(com, args)
        except BaseException:
            self.logger.log_error_data()
            self.close()

            return
