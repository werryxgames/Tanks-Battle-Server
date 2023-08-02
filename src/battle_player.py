"""Module for player in battle."""
from absolute import to_absolute
from mjson import read


class BattlePlayer:
    """Class for player in battle."""

    def __init__(
        self,
        nick,
        position,
        rotation,
        tank,
        gun_rotation,
        durability
    ):
        """Player in battle initalization."""
        self.nick = nick
        self.position = position
        self.rotation = rotation
        self.tank = tank
        self.gun_rotation = gun_rotation
        self.durability = durability
        self.last_damage = None

    @staticmethod
    def st_get_tank(tank):
        """Returns tank."""
        data = read(to_absolute("data.json"))

        if data is None:
            return None

        tank_data = data["tanks"][tank]["tank"]
        return tank_data

    def get_tank(self):
        """Returns current tank of player."""
        return self.st_get_tank(self.tank)

    @staticmethod
    def st_get_gun(tank):
        """Returns gun of player."""
        data = read(to_absolute("data.json"))

        if data is None:
            return None

        gun_data = data["tanks"][tank]["gun"]
        return gun_data

    def get_gun(self):
        """Returns current gun of player."""
        return self.st_get_gun(self.tank)

    def json(self):
        """Returns data in JSON-serializable format."""
        return self.__dict__
