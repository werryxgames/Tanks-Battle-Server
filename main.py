from mjson import read
from network import start_server
from logger import Logger
from singleton import set_data
from tests import tests


def main():
    logger = Logger(Logger.LEVEL_INFO, Logger.LEVEL_INFO)
    config = read("config.json")

    if tests.main(True):
        try:
            set_data(config, logger)

            start_server()

        except BaseException as e:
            logger.critical(e)
            if config["debug"]:
                raise
    else:
        logger.critical("Один из тестов провален")


if __name__ == '__main__':
    main()
