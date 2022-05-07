from mjson import read


class BattlePlayer:
    def __init__(
        self,
        nick,
        position,
        rotation,
        tank,
        gun_rotation,
        gun
    ):
        self.nick = nick
        self.position = position
        self.rotation = rotation
        self.tank = tank
        self.gun_rotation = gun_rotation
        self.gun = gun

    def get_tank(self):
        data = read("data.json")
        if data is None:
            return

        tank_data = data["tanks"][self.tank]
        res_data = {}
        for k, v in tank_data.items():
            if k in ["durability", "mass", "speed", "gravity", "rotation_speed", "gun_rotation_speed"]:
                res_data[k] = v

        return res_data 

    def get_gun(self):
        data = read("data.json")
        if data is None:
            return

        gun_data = data["guns"][self.gun]
        res_data = {}
        for k, v in gun_data.items():
            if k in ["damage", "rotation_speed", "shot_speed"]:
                res_data[k] = v

        return res_data 

    def json(self):
        return self.__dict__
