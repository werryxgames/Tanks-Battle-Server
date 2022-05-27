from json import loads, dumps
from random import choice
from threading import Thread
from time import sleep
from datetime import datetime
from accounts import AccountManager
from singleton import get_data, get_clients
from mjson import read
from battle_player import BattlePlayer
from message import GlobalMessage

clients = get_clients()


class Player:
    BACK_TO_MENU = 1

    def __init__(self, sock, addr, battle_data, rudp):
        self.sock = sock
        self.addr = addr
        self.bdata = battle_data
        self.rudp = rudp
        self.config, self.logger = get_data()[:2]
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
        self.still_check_time = False

        try:
            self.send(["something_wrong"])
            clients.pop(self.addr)
            self.logger.info(f"Клиент '{self.bp.nick}' ('{self.addr[0]}:{self.addr[1]}') отключён")
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

    def send(self, *args, **kwargs):
        self.rudp.send(*args, **kwargs)

    def send_unreliable(self, *args, **kwargs):
        self.rudp.send_unreliable(*args, **kwargs)

    def handle_messages(self):
        mesgs = self.bdata["messages"]
        if len(mesgs) > self.msg:
            msg = mesgs[-1].get()
            if msg[0] == "player_leave":
                if msg[1] != self.bp.nick:
                    self.send(["player_leave", msg[1]])
                else:
                    self.close()
            elif msg[0] == "player_join":
                if msg[1][0] != self.bp.nick:
                    self.send(["player_join", msg[1][1:]])
            elif msg[0] == "player_shoot":
                if msg[1][0] != self.bp.nick:
                    player = None

                    for pl in self.bdata["players"]:
                        if pl.nick == msg[1][0]:
                            player = pl

                            break

                    if player is not None:
                        gun = player.get_gun()
                        self.send(["player_shoot", msg[1][1][0], msg[1][1][1], gun["shot_speed"], gun["damage"], msg[1][0]])
            self.msg += 1

    def randpoint(self):
        return choice(self.map["spawn_points"])

    def check_time(self):
        while self.still_check_time:
            if datetime.today().timestamp() - self.config["max_player_noresponse_time"] > self.last_request:
                self.bdata["players"].remove(self.bp)
                self.bdata["messages"].append(GlobalMessage("player_leave", self.bp.nick))

                self.close()

                self.logger.debug(f"Игрок '{self.bp.nick}' отключён из-за неактивности")

            sleep(1)

    def receive(self, jdt):
        try:
            if self.bp is not None:
                self.handle_messages()

            self.last_request = datetime.today().timestamp()

            com = jdt[0]
            args = jdt[1:]

            if com == "get_battle_data":
                self.refresh_account()

                self.map = read("data.json")["maps"][self.bdata["map"]]

                self.bp = BattlePlayer(
                    self.account["nick"],
                    self.randpoint(),
                    (0, 0, 0),
                    self.account["selected_tank"],
                    (0, 0, 0),
                    self.account["selected_gun"],
                    BattlePlayer.st_get_tank(self.account["selected_tank"])["durability"]
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

                self.bdata["messages"].append(GlobalMessage("player_join", [self.bp.nick, self.bp.json(), self.bp.get_tank(), self.bp.get_gun()]))

                Thread(target=self.check_time).start()

            elif com == "request_tanks_data":
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
                    else:
                        self.send(["respawn", self.randpoint(), BattlePlayer.st_get_tank(self.account["selected_tank"])["durability"], self.respawn_id])
                else:
                    if self.bp.last_damage is not None:
                        killer = AccountManager.get_account(self.bp.last_damage)

                        if killer not in [AccountManager.FAILED_UNKNOWN, AccountManager.FAILED_NOT_FOUND]:
                            AccountManager.set_account(self.bp.last_damage, "crystals", killer["crystals"] + self.config["kill_reward_crystals"])
                            AccountManager.set_account(self.bp.last_damage, "xp", killer["xp"] + self.config["kill_reward_xp"])
                    self.send(["respawn", self.randpoint(), BattlePlayer.st_get_tank(self.account["selected_tank"])["durability"], self.respawn_id])

            elif com == "leave_battle":
                self.bdata["players"].remove(self.bp)
                self.bdata["messages"].append(GlobalMessage("player_leave", self.bp.nick))

                self.close()

                return

            elif com == "leave_battle_menu":
                self.bdata["players"].remove(self.bp)
                self.bdata["messages"].append(GlobalMessage("player_leave", self.bp.nick))

                self.still_check_time = False

                return self.BACK_TO_MENU

            elif com == "shoot":
                self.bdata["messages"].append(GlobalMessage("player_shoot", [self.bp.nick, args[0]]))

            elif com == "damaged_by":
                self.bp.last_damage = args[0]

            elif com == "respawned":
                self.respawn_id = args[0] + 1

        except:
            self.logger.log_error_data()
            self.close()

            return
