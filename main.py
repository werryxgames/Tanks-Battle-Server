from mjson import read
from network import start_tcp_server
from logger import Logger
from singleton import set_data


def main():
    logger = Logger(Logger.LEVEL_DEBUG, Logger.LEVEL_DEBUG)

    try:
        config = read("config.json")
        set_data(config, logger)

        start_tcp_server()

    except BaseException as e:
        logger.error(e)


if __name__ == '__main__':
    main()
