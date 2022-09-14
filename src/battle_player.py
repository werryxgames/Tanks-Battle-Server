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
        durability
    ):
        """Инициализация игрока в битве."""
        self.nick = nick
        self.position = position
        self.rotation = rotation
        self.tank = tank
        self.gun_rotation = gun_rotation
        self.durability = durability
        self.last_damage = None

    @staticmethod
    def st_get_tank(tank):
        """Возвращает корпус."""
        data = read(to_absolute("data.json"))

        if data is None:
            return None

        tank_data = data["tanks"][tank]["tank"]
        return tank_data

    def get_tank(self):
        """Возвращает текущий корпус игрока."""
        return self.st_get_tank(self.tank)

    @staticmethod
    def st_get_gun(tank):
        """Возвращает башню игрока."""
        data = read(to_absolute("data.json"))

        if data is None:
            return None

        gun_data = data["tanks"][tank]["gun"]
        return gun_data

    def get_gun(self):
        """Возвращает текущую башню игрока."""
        return self.st_get_gun(self.tank)

    def json(self):
        """Возвращает данные в формате, для преобразования в JSON."""
        return self.__dict__
