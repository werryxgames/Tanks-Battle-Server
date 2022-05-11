from json import loads, dumps
from random import choice
from accounts import AccountManager
from singleton import get_data, get_clients
from mjson import read
from battle_player import BattlePlayer
from message import GlobalMessage

clients = get_clients()


class Player:
    BACK_TO_MENU = 1

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
        self.msg = len(battle_data["messages"])

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
        return choice(read("data.json")["maps"][self.bdata["map"]]["spawn_points"])

    def receive(self, data):
        try:
            jdt = loads(data.decode("utf8"))

            self.handle_messages()

            com = jdt[0]
            args = jdt[1:]

            if com == "get_battle_data":
                self.refresh_account()

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

            elif com == "request_tanks_data":
                if args[3] > 0:
                    self.bp.position = args[0]
                    self.bp.rotation = args[1]
                    self.bp.gun_rotation = args[2]
                    self.bp.durability = args[3]

                    players = self.bdata["players"]
                    res = []
                    for pl in players:
                        if pl is not self.bp:
                            res.append([pl.json()])

                    self.send(["tanks_data", res])
                else:
                    if self.bp.last_damage is not None:
                        killer = AccountManager.get_account(self.bp.last_damage)
                        if killer not in [AccountManager.FAILED_UNKNOWN, AccountManager.FAILED_NOT_FOUND]:
                            AccountManager.set_account(self.bp.last_damage, "crystals", killer["crystals"] + self.config["kill_reward_crystals"])
                            AccountManager.set_account(self.bp.last_damage, "xp", killer["xp"] + self.config["kill_reward_xp"])
                    self.send(["respawn", self.randpoint(), BattlePlayer.st_get_tank(self.account["selected_tank"])["durability"]])

            elif com == "leave_battle":
                self.bdata["players"].remove(self.bp)
                self.bdata["messages"].append(GlobalMessage("player_leave", self.bp.nick))

                self.close()
                return

            elif com == "leave_battle_menu":
                self.bdata["players"].remove(self.bp)
                self.bdata["messages"].append(GlobalMessage("player_leave", self.bp.nick))
                return self.BACK_TO_MENU

            elif com == "shoot":
                self.bdata["messages"].append(GlobalMessage("player_shoot", [self.bp.nick, args[0]]))

            elif com == "damaged_by":
                self.bp.last_damage = args[0]

        except BaseException as e:
            self.logger.error(e)
            self.close()
            if self.config["debug"]:
                raise
            return
