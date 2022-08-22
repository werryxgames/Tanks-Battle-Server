"""Модуль синглтона."""
from random import randint

from mjson import read


class Singleton:
    """Класс синглтона."""
    config = None
    logger = None
    win = None
    matches = []
    clients = {}

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Singleton, cls).__new__(cls)

        return cls.instance


st = Singleton()


def set_data(config=None, logger=None, win=None):
    """Устанавливает данные в синглтон."""
    if config is not None:
        st.config = config

    if logger is not None:
        st.logger = logger

    if win is not None:
        st.win = win


def get_data():
    """Получает данные из синглтона."""
    data = []

    if st.config is not None:
        data.append(st.config)
    if st.config is not None:
        data.append(st.logger)
    if st.win is not None:
        data.append(st.win)

    return data


def add_match(name, max_players, creator):
    """Добавляет матч."""
    maps = read("data.json")["maps"]

    battle = {
        "name": name,
        "max_players": max_players,
        "creator": creator,
        "players": [],
        "map": randint(0, len(maps) - 1),
        "messages": []
    }

    st.matches.append(battle)

    return battle


def get_matches():
    """Возвращает список всех матчей."""
    return st.matches


def remove_match(name):
    """Удаляет матч."""
    try:
        for battle in st.matches:
            if battle["name"] == name:
                st.matches.remove(battle)

                return True
    except (AttributeError, IndexError):
        pass

    return False


def get_clients():
    """Возвращает список всех клиентов."""
    return st.clients
