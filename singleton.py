from random import randint


class Singleton(object):
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
		"players": 0,
		"map": randint(0, st.config["maps"] - 1)
	}

	try:
		st.matches.append(battle)
	except AttributeError:
		st.matches = [battle]

	return battle


def get_matches():
	try:
		return st.matches
	except AttributeError:
		return []


def remove_match(name):
	try:
		for battle in st.matches:
			if battle["name"] == name:
				st.matches.remove(battle)
				return True
	except (AttributeError, IndexError):
		pass
	return False
