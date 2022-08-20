"""Модуль игрока в битве."""
from absolute import to_absolute
from mjson import read


class BattlePlayer:
    """Класс игрока в битве."""

    def __init__(
        self,
        nick,
        position,
        rotation,
        tank,
        gun_rotation,
        gun,
        durability,
        tank_pt
    ):
        self.nick = nick
        self.position = position
        self.rotation = rotation
        self.tank = tank
        self.gun_rotation = gun_rotation
        self.gun = gun
        self.durability = durability
        self.tank_pt = tank_pt
        self.last_damage = None

    @staticmethod
    def st_get_tank(tank, tank_pt):
        """Возвращает танк."""
        data = read(to_absolute("data.json"))

        if data is None:
            return None

        if tank_pt == -1:
            tank_data = data["tanks"][tank]
        else:
            tank_data = data["pts"][tank_pt]["tank"]

        res_data = {}

        for key, value in tank_data.items():
            if key in [
                "durability",
                "mass",
                "speed",
                "gravity",
                "rotation_speed",
                "gun_rotation_speed"
            ]:
                res_data[key] = value

        return res_data

    def get_tank(self):
        """Возвращает текущий танк игрока."""
        return self.st_get_tank(self.tank, self.tank_pt)

    def get_gun(self):
        """Возвращает текущую башню игрока."""
        data = read("data.json")

        if data is None:
            return None

        if self.tank_pt == -1:
            gun_data = data["guns"][self.gun]
        else:
            gun_data = data["pts"][self.tank_pt]["gun"]

        res_data = {}

        for key, value in gun_data.items():
            if key in [
                "damage",
                "rotation_speed",
                "shot_speed",
                "damage",
                "recoil",
                "recharge"
            ]:
                res_data[key] = value

        return res_data

    def json(self):
        """Возвращает данные в формате, для преобразования в JSON."""
        return self.__dict__
