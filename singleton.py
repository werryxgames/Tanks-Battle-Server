from random import randint


class Singleton:
    config = None
    logger = None
    matches = []
    clients = {}

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance


st = Singleton()


def set_data(config=None, logger=None):
    if config is not None:
        st.config = config
    if logger is not None:
        st.logger = logger


def get_data():
    return (st.config, st.logger)


def add_match(name, max_players, creator):
    battle = {
        "name": name,
        "max_players": max_players,
        "creator": creator,
        "players": [],
        "map": randint(0, st.config["maps"] - 1),
        "messages": []
    }

    st.matches.append(battle)

    return battle


def get_matches():
    return st.matches


def remove_match(name):
    try:
        for battle in st.matches:
            if battle["name"] == name:
                st.matches.remove(battle)
                return True
    except (AttributeError, IndexError):
        pass
    return False


def get_clients():
    return st.clients
