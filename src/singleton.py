"""Singleton module."""
from mjson import read


class Singleton:
    """Singleton class."""

    config = None
    logger = None
    win = None
    matches = []
    clients = {}

    def __new__(cls):
        """Returns instance of singleton."""
        if not hasattr(cls, "instance"):
            cls.instance = super(Singleton, cls).__new__(cls)

        return cls.instance


st = Singleton()


def set_data(config=None, logger=None, win=None):
    """Sets data to singleton."""
    if config is not None:
        st.config = config

    if logger is not None:
        st.logger = logger

    if win is not None:
        st.win = win


def get_data():
    """Gets data from singleton."""
    return [st.config, st.logger, st.win]


def add_match(map_id, max_players):
    """Adds match."""
    battle = {
        "max_players": max_players,
        "players": [],
        "map": map_id,
        "messages": []
    }
    st.matches.append(battle)
    return battle


def get_matches():
    """Returns list of all matches."""
    return st.matches


def remove_match(name):
    """Removes match from list."""
    try:
        st.matches[name] = None
    except IndexError:
        return False

    return True


def get_clients():
    """Returns list of all clients."""
    return st.clients


def get_const_params():
    """Returns all constant parameters."""
    params = st.config["constant_params"]
    maps = read("data.json")["maps"]
    params["maps"] = [map_["name"] for map_ in maps]
    return params
