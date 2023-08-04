"""Tanks Battle client."""
from copy import deepcopy

from accounts import AccountManager
from custom_structs import MapStruct
from custom_structs import RankStruct
from custom_structs import TankStruct
from mjson import read
from netclasses import NetUser
from player import Player
from serializer import ByteBuffer
from singleton import add_match
from singleton import get_clients
from singleton import get_data
from singleton import get_maps
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
            self.send(ByteBuffer(2).put_16(2).to_bytes())
            clients.pop(self.addr)
            self.logger.info(
                f"Client '{self.account['nick']}' ('{self.addr[0]}:\
{self.addr[1]}') disconnected")
        except OSError:
            pass

    def redirect_to_player(self, code, data):
        """Redirects packet to Player, if possible."""
        if self.send_player:
            if self.player.receive(code, data) == Player.BACK_TO_MENU:
                self.send_player = False
                self.player = None

            return True
        return False

    def handle_account(self, code, _data):
        """Handles data of client's account."""
        if code == 2:
            self.refresh_account()

            ranks_size_sum: int = 0
            ranks_array: list = []

            for rank in self.config["ranks"]:
                rank_struct = RankStruct(rank)
                ranks_array.append(rank_struct)
                ranks_size_sum += rank_struct.__bb_size__()

            maps_size_sum: int = 0
            maps_array: list = []

            for map_ in get_maps():
                map_struct = MapStruct(map_)
                maps_array.append(map_struct)
                maps_size_sum += map_struct.__bb_size__()

            buffer: ByteBuffer = ByteBuffer(
                2 + 2 + ranks_size_sum + 4 + 4 + 2 + maps_size_sum
            )
            (
                buffer
                .put_u16(11)
                .put_u16(len(ranks_array))
            )

            for rank in ranks_array:
                buffer.put_struct(rank)

            (
                buffer
                .put_u32(self.account["xp"])
                .put_32(self.account["crystals"])
                .put_u16(len(maps_array))
            )

            for map_ in maps_array:
                buffer.put_struct(map_)

            self.send(buffer.to_bytes())
            return True

        return False

    def update_client_data(self, fail_data):
        """Updates client data."""
        data = read("../data.json")

        if data is None:
            self.send(fail_data)
            return

        self.refresh_account()

        # First argument is False, because it doesn't impact size
        tanks = ByteBuffer(4 + sum([TankStruct(tank, False).__bb_size__() for tank in data["tanks"]]))
        tanks.put_u32(len(data["tanks"]))

        for i, tank_ in enumerate(data["tanks"]):
            tanks.put_struct(TankStruct(tank_, i in self.account["tanks"]))

        self.send(
            ByteBuffer(2 + tanks.size() + 4 + 4)
            .put_u16(13)
            .put_bytes(tanks.to_bytes())
            .put_u32(self.account["selected_tank"])
            .put_32(self.account["crystals"])
            .to_bytes()
        )

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

    def handle_hangar(self, code, data):
        """Handles hangar data of client."""
        if code == 3:
            self.update_client_data(ByteBuffer(2).put_16(12).to_bytes())
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

        if self.handle_hangar(code, data):
            return

        if self.handle_matches(code, data):
            return

        if self.handle_settings(code, data):
            return

    def receive(self, code, data):
        """Received client's packet."""
        if self.redirect_to_player(code, data):
            return

        try:
            self.handle(code, data)
        except BaseException:
            self.logger.log_error_data()
            self.close()
            return
