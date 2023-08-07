"""Module for player."""
from datetime import datetime
from random import choice
from threading import Thread
from time import sleep

from accounts import AccountManager
from battle_player import BattlePlayer
from custom_structs import BattlePlayerStruct
from custom_structs import BattleDataStruct
from custom_structs import BattleTankStruct
from custom_structs import SettingsStruct
from custom_structs import BattlePlayerDataStruct
from message import GlobalMessage
from mjson import read
from netclasses import NetUser
from singleton import get_clients
from serializer import ByteBuffer

clients = get_clients()


class Player(NetUser):
    """Class for player."""

    BACK_TO_MENU = 1

    def __init__(self, sock, addr, battle_data, rudp):
        """Player in match initialization."""
        self.sock = sock
        self.addr = addr
        self.bdata = battle_data

        super().__init__(rudp)

        self.version = None
        self.bp = None
        self.msg = len(battle_data["messages"])
        self.last_request = -1
        self.still_check_time = True
        self.map = None

    def close(self):
        """Closes connection with client."""
        self.still_check_time = False

        try:
            self.send(ByteBuffer(2).put_16(2).to_bytes())
            clients.pop(self.addr)
            self.logger.info(
                f"Client '{self.bp.nick}' ('{self.addr[0]}:{self.addr[1]}') \
disconnected"
            )
        except OSError:
            pass

    def send_unreliable(self, *args, **kwargs):
        """Sends Unreliable UDP data to client."""
        self.rudp.send_unreliable(*args, **kwargs)

    def on_player_shoot(self, msg):
        """Handles shoot message from player."""
        player = None

        for pl in self.bdata["players"]:
            if pl.nick == msg[0]:
                player = pl
                break

        if player is not None:
            gun = player.get_gun()
            self.send(
                ByteBuffer(70 + len(msg[0].encode("UTF-8")) + 1)
                .put_float(msg[1][0])
                .put_float(msg[1][1])
                .put_float(msg[1][2])
                .put_float(msg[2][0][0])
                .put_float(msg[2][0][1])
                .put_float(msg[2][0][2])
                .put_float(msg[2][1][0])
                .put_float(msg[2][1][1])
                .put_float(msg[2][1][2])
                .put_float(msg[2][2][0])
                .put_float(msg[2][2][1])
                .put_float(msg[2][2][2])
                .put_float(msg[2][3][0])
                .put_float(msg[2][3][1])
                .put_float(msg[2][3][2])
                .put_float(gun["shot_speed"])
                .put_float(gun["damage"])
                .put_string(msg[0])
                .to_bytes()
            )

    def handle_messages(self):
        """Handles global messages."""
        mesgs = self.bdata["messages"]

        if len(mesgs) > self.msg:
            msg = mesgs[-1].get()

            if msg[0] == "player_leave":
                if msg[1] != self.bp.nick:
                    self.send(
                        ByteBuffer(2 + len(msg[1].encode("UTF-8")) + 1)
                        .put_string(msg[1])
                        .to_bytes()
                    )
            elif msg[0] == "player_join":
                if msg[1][0].player[0] != self.bp.nick:
                    self.send(
                        ByteBuffer(2 + msg[1][0].__bb_size__(
                        ) + msg[1][1].__bb_size__())
                        .put_u16(25)
                        .put_struct(msg[1][0])
                        .put_struct(msg[1][1])
                        .to_bytes()
                    )
            elif msg[0] == "player_shoot":
                if msg[1][0] != self.bp.nick:
                    self.on_player_shoot(msg[1])

            self.msg += 1

    def randpoint(self):
        """Handles random spawn point."""
        return choice(self.map["spawn_points"])

    def check_time(self):
        """Checks inactive time of player."""
        while self.still_check_time:
            if datetime.today().timestamp() - \
                    self.config["max_player_noresponse_time"] > \
                    self.last_request:
                self.bdata["players"].remove(self.bp)
                self.bdata["messages"].append(GlobalMessage(
                    "player_leave",
                    self.bp.nick
                ))

                self.close()

                self.logger.debug(
                    f"Player '{self.bp.nick}' kicked due to inactivity"
                )

            sleep(1)

    def receive_get_batte_data(self):
        """Receives battle data."""
        self.refresh_account()
        self.map = read("../data.json")["maps"][self.bdata["map"]]
        tank = BattlePlayer.st_get_tank(
            self.account["selected_tank"]
        )
        gun = BattlePlayer.st_get_gun(
            self.account["selected_tank"]
        )
        self.bp = BattlePlayer(
            self.account["nick"],
            self.randpoint(),
            (0, 0, 0),
            self.account["selected_tank"],
            (
                0,
                gun["default_rotation"],
                0
            ) if "default_rotation" in gun else (0, 0, 0),
            BattlePlayer.st_get_tank(
                self.account["selected_tank"]
            )["durability"]
        )
        self.bdata["players"].append(self.bp)
        pls = []

        for bp in self.bdata["players"]:
            pls.append([
                BattlePlayerStruct(bp.arr()),
                BattleTankStruct({"tank": tank, "gun": gun})
            ])

        # cast to str because on client it is string concatenation
        bdata = BattleDataStruct([
            str(self.bdata["map"]),
            pls[-1],
            pls[:-1],
            SettingsStruct(self.account["settings"])
        ])
        pck = ByteBuffer(2 + bdata.__bb_size__())
        pck.put_u16(23)
        pck.put_struct(bdata)
        self.send(pck.to_bytes())

        self.bdata["messages"].append(GlobalMessage(
            "player_join",
            [
                BattlePlayerStruct(self.bp.arr()),
                BattleTankStruct(
                    {"tank": self.bp.get_tank(), "gun": self.bp.get_gun()}
                )
            ]
        ))

        Thread(target=self.check_time).start()

    def receive_request_tanks_data(self, data):
        """Receives requested data of tanks."""
        tank_data = data.get_struct(BattlePlayerDataStruct)

        if tank_data[9] > 0:
            if tank_data[1] > self.map["kill_y"]:
                self.bp.position = [tank_data[0], tank_data[1], tank_data[2]]
                self.bp.rotation = [tank_data[3], tank_data[4], tank_data[5]]
                self.bp.gun_rotation = [
                    tank_data[6],
                    tank_data[7],
                    tank_data[8]
                ]
                self.bp.durability = tank_data[9]

                players = self.bdata["players"]
                res = []
                sum_size: int = 0

                for pl in players:
                    if pl is not self.bp:
                        bp: BattlePlayerStruct = BattlePlayerStruct(pl.arr())
                        sum_size += bp.__bb_size__()
                        res.append(bp)

                buffer: ByteBuffer = ByteBuffer(3 + sum_size)
                buffer.put_u16(24)
                buffer.put_u8(len(res))

                for pl in res:
                    buffer.put_struct(pl)

                self.send_unreliable(buffer.to_bytes())
                return None

            randpoint = self.randpoint()
            self.send(
                ByteBuffer(18)
                .put_u16(27)
                .put_u32(self.bp.get_tank()["durability"])
                .put_float(randpoint[0])
                .put_float(randpoint[1])
                .put_float(randpoint[2])
                .to_bytes()
            )
            return None

        if self.bp.last_damage is not None:
            killer = AccountManager.get_account(
                self.bp.last_damage
            )

            if killer not in [
                AccountManager.FAILED_UNKNOWN,
                AccountManager.FAILED_NOT_FOUND
            ]:
                AccountManager.set_account(
                    self.bp.last_damage,
                    "crystals",
                    killer["crystals"] + self.config[
                        "kill_reward_crystals"
                    ]
                )
                AccountManager.set_account(
                    self.bp.last_damage,
                    "xp",
                    killer["xp"] + self.config["kill_reward_xp"]
                )

            self.bp.last_damage = None

        randpoint = self.randpoint()
        self.send(
            ByteBuffer(18)
            .put_u16(27)
            .put_u32(self.bp.get_tank()["durability"])
            .put_float(randpoint[0])
            .put_float(randpoint[1])
            .put_float(randpoint[2])
            .to_bytes()
        )
        self.bp.durability = -1
        return None

    def try_handle_messages(self):
        """Handles messages."""
        if self.bp is not None:
            self.handle_messages()

    def receive(self, code, data):
        """Handles client data."""
        try:
            self.try_handle_messages()
            self.last_request = datetime.today().timestamp()

            if code == 14:
                self.receive_get_batte_data()
                return None

            if code == 16:
                self.receive_request_tanks_data(data)
                return None

            if code == 7:
                self.bdata["players"].remove(self.bp)
                self.bdata["messages"].append(GlobalMessage(
                    "player_leave",
                    self.bp.nick
                ))
                self.still_check_time = False
                return None

            if code == 11:
                self.bdata["players"].remove(self.bp)
                self.bdata["messages"].append(GlobalMessage(
                    "player_leave",
                    self.bp.nick
                ))
                self.still_check_time = False
                return self.BACK_TO_MENU

            if code == 18:
                self.bdata["messages"].append(GlobalMessage(
                    "player_shoot",
                    [
                        self.bp.nick,
                        [data.get_float(), data.get_float(), data.get_float()],
                        [
                            [
                                data.get_float(),
                                data.get_float(),
                                data.get_float()
                            ],
                            [
                                data.get_float(),
                                data.get_float(),
                                data.get_float()
                            ],
                            [
                                data.get_float(),
                                data.get_float(),
                                data.get_float()
                            ],
                            [
                                data.get_float(),
                                data.get_float(),
                                data.get_float()
                            ]
                        ]
                    ]
                ))
                return None

            if code == 17:
                self.bp.last_damage = data.get_u16()
                return None

        except BaseException:
            self.logger.log_error_data()
            self.close()

        return None
