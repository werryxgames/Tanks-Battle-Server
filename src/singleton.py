"""Singleton module."""
from mjson import read


class Singleton:
    """Singleton class."""

    config = None
    logger = None
    win = None
    matches = []
    clients = {}
    run_file = None

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


def get_maps():
    """Returns all constant parameters."""
    maps = read("../data.json")["maps"]
    return maps


def set_run_file(run_file):
    """Sets 'run' file, used to indicate if server is running."""
    st.run_file = run_file


def get_run_file():
    """Gets 'run' file. See `set_run_file` for more information."""
    return st.run_file
