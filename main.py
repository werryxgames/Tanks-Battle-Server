from mjson import read
from network import start_server
from logger import Logger
from singleton import set_data
from tests import tests
from console import ConsoleExecutor


def main():
    logger = Logger(Logger.LEVEL_INFO, Logger.LEVEL_INFO)
    config = read("config.json")

    if tests.main(True):
        try:
            set_data(config, logger)

            start_server()

        except:
            logger.log_error_data(logger.critical)
    else:
        logger.critical("Один из тестов провален")


if __name__ == '__main__':
    main()
