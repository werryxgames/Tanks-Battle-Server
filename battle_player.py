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
        durability,
        pt
    ):
        self.nick = nick
        self.position = position
        self.rotation = rotation
        self.tank = tank
        self.gun_rotation = gun_rotation
        self.gun = gun
        self.durability = durability
        self.pt = pt
        self.last_damage = None

    @staticmethod
    def st_get_tank(tank, pt):
        data = read(to_absolute("data.json"))

        if data is None:
            return

        if pt == -1:
            tank_data = data["tanks"][tank]
        else:
            tank_data = data["pts"][pt]["tank"]

        res_data = {}

        for k, v in tank_data.items():
            if k in ["durability", "mass", "speed", "gravity", "rotation_speed", "gun_rotation_speed"]:
                res_data[k] = v

        return res_data

    def get_tank(self):
        return self.st_get_tank(self.tank, self.pt)

    def get_gun(self):
        data = read("data.json")

        if data is None:
            return

        if self.pt == -1:
            gun_data = data["guns"][self.gun]
        else:
            gun_data = data["pts"][self.pt]["gun"]

        res_data = {}

        for k, v in gun_data.items():
            if k in ["damage", "rotation_speed", "shot_speed", "damage", "recoil", "recharge"]:
                res_data[k] = v

        return res_data

    def json(self):
        return self.__dict__
