from json import dumps
from mjson import read


class BattlePlayer:
    def __init__(
        self,
        nick,
        position,
        rotation,
        tank
    ):
        self.nick = nick
        self.position = position
        self.rotation = rotation
        self.tank = tank

    def get_tank(self):
        data = read("data.json")
        if data is None:
            return

        tank_data = data["tanks"][self.tank]
        res_data = {}
        for k, v in tank_data.items():
            if k in ["durability", "mass", "speed", "gravity", "rotation_speed"]:
                res_data[k] = v

        return res_data 

    def json(self):
        return self.__dict__
