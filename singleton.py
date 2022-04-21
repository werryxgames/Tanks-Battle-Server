class Singleton(object):
	def __new__(cls):
		if not hasattr(cls, "instance"):
			cls.instance = super(Singleton, cls).__new__(cls)
		return cls.instance


def set_data(config=None, logger=None):
	st = Singleton()

	if config is not None:
		st.config = config
	if logger is not None:
		st.logger = logger


def get_data():
	st = Singleton()
	return (st.config, st.logger)


def add_match(name, max_players, creator):
	st = Singleton()
	battle = {
		"name": name,
		"max_players": max_players,
		"creator": creator,
		"players": 0
	}

	try:
		st.matches.append(battle)
	except AttributeError:
		st.matches = [battle]


def get_matches():
	try:
		st = Singleton()
		return st.matches
	except AttributeError:
		return []
