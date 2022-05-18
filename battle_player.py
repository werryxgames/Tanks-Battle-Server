from absolute import to_absolute
from mjson import read


class BattlePlayer:
    def __init__(
        self,
        nick,
        position,
        rotation,
        tank,
        gun_rotation,
        gun,
        durability
    ):
        self.nick = nick
        self.position = position
        self.rotation = rotation
        self.tank = tank
        self.gun_rotation = gun_rotation
        self.gun = gun
        self.durability = durability
        self.last_damage = None

    @staticmethod
    def st_get_tank(tank):
        data = read(to_absolute("data.json"))

        if data is None:
            return

        tank_data = data["tanks"][tank]
        res_data = {}

        for k, v in tank_data.items():
            if k in ["durability", "mass", "speed", "gravity", "rotation_speed", "gun_rotation_speed"]:
                res_data[k] = v

        return res_data

    def get_tank(self):
        return self.st_get_tank(self.tank)

    def get_gun(self):
        data = read("data.json")

        if data is None:
            return

        gun_data = data["guns"][self.gun]
        res_data = {}

        for k, v in gun_data.items():
            if k in ["damage", "rotation_speed", "shot_speed", "damage", "recoil", "recharge"]:
                res_data[k] = v

        return res_data

    def json(self):
        return self.__dict__
