"""Модуль игрока."""
from datetime import datetime
from random import choice
from threading import Thread
from time import sleep

from accounts import AccountManager
from battle_player import BattlePlayer
from message import GlobalMessage
from mjson import read
from singleton import get_clients
from singleton import get_data

clients = get_clients()


class Player:
    """Класс игрока."""
    BACK_TO_MENU = 1

    def __init__(self, sock, addr, battle_data, rudp):
        self.sock = sock
        self.addr = addr
        self.bdata = battle_data
        self.rudp = rudp

        data = get_data()
        self.config = data[0]
        self.logger = data[1]

        self.version = None
        self.login = None
        self.password = None
        self.account = None
        self.bp = None
        self.msg = len(battle_data["messages"])
        self.last_request = -1
        self.still_check_time = True
        self.map = None
        self.respawn_id = 0

    def close(self):
        """Закрывает соединение с клиентом."""
        self.still_check_time = False

        try:
            self.send(["something_wrong"])
            clients.pop(self.addr)
            self.logger.info(
                f"Клиент '{self.bp.nick}' ('{self.addr[0]}:{self.addr[1]}') \
отключён"
            )
        except OSError:
            pass

    def set_login_data(self, login, password):
        """Устанавливает данные для авторизации."""
        self.login = login
        self.password = password
        self.account = AccountManager.get_account(login)

        if self.account == AccountManager.FAILED_UNKNOWN or \
                self.account == AccountManager.FAILED_NOT_FOUND or \
                self.account["password"] != password:
            return False

        return True

    def refresh_account(self):
        """Перезагружает аккаунт."""
        self.account = AccountManager.get_account(self.login)

        if self.account == AccountManager.FAILED_UNKNOWN or \
                self.account == AccountManager.FAILED_NOT_FOUND or \
                self.account["password"] != self.password:
            return False

        return True

    def send(self, *args, **kwargs):
        """Отправляет Reliable UDP данные клиенту."""
        self.rudp.send(*args, **kwargs)

    def send_unreliable(self, *args, **kwargs):
        """Отправляет Unreliable UDP данные клиенту."""
        self.rudp.send_unreliable(*args, **kwargs)

    def on_player_shoot(self, msg):
        """Обрабатывает сообщение стрельбы другого игрока."""
        player = None

        for pl in self.bdata["players"]:
            if pl.nick == msg[1][0]:
                player = pl
                break

        if player is not None:
            gun = player.get_gun()
            self.send([
                "player_shoot",
                msg[1][1][0],
                msg[1][1][1],
                gun["shot_speed"],
                gun["damage"],
                msg[1][0]
            ])

    def handle_messages(self):
        """Обрабатывает глобальные сообщения."""
        mesgs = self.bdata["messages"]

        if len(mesgs) > self.msg:
            msg = mesgs[-1].get()

            if msg[0] == "player_leave":
                if msg[1] != self.bp.nick:
                    self.send(["player_leave", msg[1]])
            elif msg[0] == "player_join":
                if msg[1][0] != self.bp.nick:
                    self.send(["player_join", msg[1][1:]])
            elif msg[0] == "player_shoot":
                if msg[1][0] != self.bp.nick:
                    self.on_player_shoot(msg)

            self.msg += 1

    def randpoint(self):
        """Возвращает случайную точку появления."""
        return choice(self.map["spawn_points"])

    def check_time(self):
        """Проверяет время неактивности игрока."""
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
                    f"Игрок '{self.bp.nick}' отключён из-за неактивности"
                )

            sleep(1)

    def receive_get_batte_data(self, args):
        """Получает данные битвы."""
        self.refresh_account()

        self.map = read("data.json")["maps"][self.bdata["map"]]

        self.bp = BattlePlayer(
            self.account["nick"],
            self.randpoint(),
            (0, 0, 0),
            self.account["selected_tank"],
            (0, 0, 0),
            self.account["selected_gun"],
            BattlePlayer.st_get_tank(
                self.account["selected_tank"],
                self.account["selected_pt"]
            )["durability"],
            self.account["selected_pt"]
        )

        self.bdata["players"].append(self.bp)

        pls = []

        for bp in self.bdata["players"]:
            pls.append([bp.json(), bp.get_tank(), bp.get_gun()])

        self.send([
            "battle_data",
            self.bdata["map"],
            pls[-1],
            pls[:-1],
            self.account["settings"]
        ])

        self.bdata["messages"].append(GlobalMessage(
            "player_join",
            [
                self.bp.nick,
                self.bp.json(),
                self.bp.get_tank(),
                self.bp.get_gun()
            ]
        ))

        Thread(target=self.check_time).start()
        return None

    def receive_request_tanks_data(self, args):
        """Получает запрошенные данные танков."""
        if args[3] > 0:
            if args[0][1] > self.map["kill_y"]:
                self.bp.position = args[0]
                self.bp.rotation = args[1]
                self.bp.gun_rotation = args[2]
                self.bp.durability = args[3]

                players = self.bdata["players"]
                res = []

                for pl in players:
                    if pl is not self.bp:
                        res.append([pl.json()])

                self.send_unreliable(["tanks_data", res])
                return None

            self.send([
                "respawn",
                self.randpoint(),
                BattlePlayer.st_get_tank(
                    self.account["selected_tank"],
                    self.account["selected_pt"]
                )["durability"],
                self.respawn_id
            ])
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

        self.send([
            "respawn",
            self.randpoint(),
            BattlePlayer.st_get_tank(
                self.account["selected_tank"],
                self.account["selected_pt"]
            )["durability"],
            self.respawn_id
        ])
        return None

    def try_handle_messages(self):
        """Обрабатывает сообщения, если имеются."""
        if self.bp is not None:
            self.handle_messages()

    def receive(self, jdt):
        """Обрабатывает данные клиента."""
        try:
            self.try_handle_messages()
            self.last_request = datetime.today().timestamp()

            com = jdt[0]
            args = jdt[1:]

            if com == "get_battle_data":
                self.receive_get_batte_data(args)
                return None

            if com == "request_tanks_data":
                self.receive_request_tanks_data(args)
                return None

            if com == "leave_battle":
                self.bdata["players"].remove(self.bp)
                self.bdata["messages"].append(GlobalMessage(
                    "player_leave",
                    self.bp.nick
                ))
                self.still_check_time = False
                return None

            if com == "leave_battle_menu":
                self.bdata["players"].remove(self.bp)
                self.bdata["messages"].append(GlobalMessage(
                    "player_leave",
                    self.bp.nick
                ))
                self.still_check_time = False
                return self.BACK_TO_MENU

            if com == "shoot":
                self.bdata["messages"].append(GlobalMessage(
                    "player_shoot",
                    [self.bp.nick, args[0]]
                ))
                return None

            if com == "damaged_by":
                self.bp.last_damage = args[0]
                return None

            if com == "respawned":
                self.respawn_id = args[0] + 1
                return None

        except BaseException:
            self.logger.log_error_data()
            self.close()

        return None
