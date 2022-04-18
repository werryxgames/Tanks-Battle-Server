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
