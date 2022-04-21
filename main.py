from mjson import read
from network import start_tcp_server
from logger import Logger
from singleton import set_data


def main():
	config = read("config.json")
	logger = Logger(Logger.LEVEL_DEBUG, Logger.LEVEL_DEBUG)
	set_data(config, logger)

	start_tcp_server()


if __name__ == '__main__':
	main()
