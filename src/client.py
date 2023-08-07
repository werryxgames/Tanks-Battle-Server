"""Tanks Battle client."""
from copy import deepcopy

from accounts import AccountManager
from custom_structs import RankStruct
from custom_structs import TankStruct
from custom_structs import SettingsStruct
from custom_structs import MatchStruct
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
                maps_array.append(map_["name"])
                maps_size_sum += len(map_["name"].encode("UTF-8")) + 1

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

            for map_name in maps_array:
                buffer.put_string(map_name)

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
        tanks = ByteBuffer(
            4 + sum(
                TankStruct(tank, False).__bb_size__() for tank in data["tanks"]
            )
        )
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

    def select_tank(self, data):
        """Handles client's request to select args[0] from type_."""
        tank_id = data.get_u32()

        if tank_id in self.account["tanks"]:
            if AccountManager.set_account(
                self.account["nick"],
                "selected_tank",
                tank_id
            ) != AccountManager.SUCCESSFUL:
                self.send(ByteBuffer(2).put_u16(14).to_bytes())
                return

            self.update_client_data(ByteBuffer(2).put_u16(14).to_bytes())
            return

        self.send(ByteBuffer(2).put_u16(14).to_bytes())
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
                    self.send(ByteBuffer(2).put_u16(2).to_bytes())
                    return

                if AccountManager.set_account(
                    self.account["nick"],
                    "tanks",
                    [*self.account["tanks"], tank_id]
                ) != AccountManager.SUCCESSFUL:
                    self.send(ByteBuffer(2).put_u16(2).to_bytes())
                    return

                if AccountManager.set_account(
                    self.account["nick"],
                    "selected_tank",
                    tank_id
                ) != AccountManager.SUCCESSFUL:
                    self.send(ByteBuffer(2).put_u16(2).to_bytes())
                    return

                self.update_client_data(ByteBuffer(2).put_u16(2).to_bytes())
                return

            self.send(ByteBuffer(2).put_u16(15).to_bytes())
            return

        self.send(ByteBuffer(2).put_u16(15).to_bytes())

    def buy_tank(self, pck):
        """Handles purchase request with data reading."""
        data = read("../data.json")

        if data is None:
            self.send(ByteBuffer(2).put_u16(2).to_bytes())
            return

        self.buy_tank_data(pck.get_u32(), data)

    def handle_tanks(self, code, data):
        """Handles client's tanks."""
        if code == 4:
            self.select_tank(data)
            return True

        if code == 5:
            self.buy_tank(data)
            return True

        return False

    def handle_hangar(self, code, data):
        """Handles hangar data of client."""
        if code == 3:
            self.update_client_data(ByteBuffer(2).put_16(12).to_bytes())
            return True

        if self.handle_tanks(code, data):
            return True

        return False

    def handle_get_matches(self):
        """Handles matches get request from client."""
        matches = get_matches()
        res = deepcopy(matches)

        # MatchStruct has constant size
        buffer: ByteBuffer = ByteBuffer(
            2 + 4 + len(res) * MatchStruct(
                {"max_players": 0, "players": 0, "map": 0}
            ).__bb_size__()
        )
        buffer.put_u16(18)
        buffer.put_u32(len(res))

        for match_ in res:
            match_["players"] = len(match_["players"])
            del match_["messages"]
            buffer.put_struct(MatchStruct(match_))

        self.send(buffer.to_bytes())

    def handle_create_match(self, data):
        """Handles match creation from client."""
        self.refresh_account()

        map_id = data.get_u16()
        max_players = data.get_u16()

        if max_players < 1 or max_players > self.config["max_play\
ers_in_game"]:
            self.send(ByteBuffer(2).put_u16(22).to_bytes())
            return

        match_ = add_match(
            map_id,
            max_players
        )

        self.send(ByteBuffer(2).put_u16(21).to_bytes())

        self.player = Player(
            self.sock,
            self.addr,
            match_,
            self.rudp
        )
        self.refresh_account()

        self.player.set_login_data(self.login, self.password)
        self.send_player = True

    def handle_join_battle(self, data):
        """Handles client join battle request."""
        matches = get_matches()
        player_match = None
        join_id: int = data.get_u16()

        for match_id, match_ in enumerate(matches):
            if match_id == join_id:
                if len(
                    match_["players"]
                ) < match_["max_players"]:
                    player_match = match_
                    self.send(ByteBuffer(2).put_u16(19).to_bytes())

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

                self.send(ByteBuffer(2).put_u16(20).to_bytes())
                return

        self.send(ByteBuffer(2).put_u16(20).to_bytes())

    def handle_matches(self, code, data):
        """Handles matches."""
        if code == 10:
            self.handle_get_matches()
            return True

        if code == 12:
            self.handle_create_match(data)
            return True

        if code == 13:
            self.handle_join_battle(data)
            return True

        return False

    def handle_settings(self, code, data):
        """Handles client's settings."""
        if code == 6:
            # SettingsStruct has constant size
            account_settings = SettingsStruct(self.account["settings"])
            buffer: ByteBuffer = ByteBuffer(2 + account_settings.__bb_size__())
            buffer.put_16(16)
            buffer.put_struct(account_settings)
            self.send(buffer.to_bytes())
            return True

        if code == 8:
            dsets = self.config["default_settings"]

            if AccountManager.set_account(
                self.account["nick"],
                "settings",
                dsets
            ) != AccountManager.SUCCESSFUL:
                self.send(ByteBuffer(2).put_u16(2))
                return True

            account_settings = SettingsStruct(self.account["settings"])
            buffer: ByteBuffer = ByteBuffer(2 + account_settings.__bb_size__())
            buffer.put_16(16)
            buffer.put_struct(account_settings)
            self.send(buffer.to_bytes())
            return True

        if code == 9:
            try:
                print(data.position, data.to_bytes())
                settings = data.get_struct(SettingsStruct)

                if 65535 > settings[2] > 10:
                    if AccountManager.set_account(
                        self.account["nick"],
                        "settings",
                        settings
                    ) != AccountManager.SUCCESSFUL:
                        self.send(ByteBuffer(2).put_u16(2).to_bytes())

                    return True

                self.send(ByteBuffer(2).put_u16(17).to_bytes())
            except ValueError:
                self.send(ByteBuffer(2).put_u16(17).to_bytes())

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
