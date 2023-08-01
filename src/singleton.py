"""Модуль синглтона."""
from mjson import read


class Singleton:
    """Класс синглтона."""

    config = None
    logger = None
    win = None
    matches = []
    clients = {}

    def __new__(cls):
        """Возвращает instance синглтона."""
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
    return [st.config, st.logger, st.win]


def add_match(map_id, max_players):
    """Добавляет матч."""
    battle = {
        "max_players": max_players,
        "players": [],
        "map": map_id,
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
        st.matches[name] = None
    except IndexError:
        return False

    return True


def get_clients():
    """Возвращает список всех клиентов."""
    return st.clients


def get_const_params():
    """Возвращает все константные параметры."""
    params = st.config["constant_params"]
    maps = read("data.json")["maps"]
    params["maps"] = [map_["name"] for map_ in maps]
    return params
