"""Модуль с тестами к Tanks Battle Server."""
from sys import path
from os import path as opath


try:
    def get_rp(file):
        """Возвращает абсолютный путь к файлу."""
        return opath.dirname(opath.realpath(file))

    rp = opath.dirname(get_rp(__file__))

    def pjoin(*args, **kwargs):
        """Соединяет пути."""
        return opath.join(*args, **kwargs)

    def to_absolute(*args, **kwargs):
        """Возвращает абсолютный путь из относительного."""
        return pjoin(rp, *args, **kwargs)

    def add_imports(ipath=""):
        """Добавляет директории импорта."""
        path.append(to_absolute(ipath))

    add_imports()
    add_imports("tests")
except IndexError:
    pass

from tester import Tester
from logger import Logger

import singleton
import mjson
import accounts


def main(quiet=False):
    """Запускает тесты."""
    # Тесты
    logger = Logger(Logger.LEVEL_DEBUG, Logger.LEVEL_NONE)
    all_passed = True

    # Синглтон
    tester = Tester(logger, singleton, quiet)
    # Ещё не вызывалось 'set_data', должен вернуть (None, None)
    tester.test("get_data", [])
    # Функция должна всегда возвращать None
    tester.test("set_data", None, "123", 456, None)
    # Функция должна вернуть то, что установила 'set_data'
    tester.test("get_data", ["123", 456, ])
    # Функция должна работать, устанавливая только одно значение
    tester.test("set_data", None, "234")
    # Функция должна работать с **kwargs
    tester.test("set_data", None, logger="789")
    # Проверка значений после 'set_data'
    tester.test("get_data", ["234", "789"])
    # Функция должна работать с **kwargs
    tester.test("set_data", None, config=905)
    # Проверка значений после 'set_data'
    tester.test("get_data", [905, "789"])
    # Установка значений для корректной работы оставшихся тестов
    config = mjson.read("config.json")
    singleton.set_data(config)

    # Матчи ещё не созданы
    tester.test("get_matches", [])
    tester.num += 1
    battle = tester.ret_value("add_match", "Test name", 10, "Test creator")
    # В результате должен быть атрибут 'map'
    tester.check_statement(battle.pop("map", False) is not False)
    tester.num += 1
    exp_battle = {
        "name": "Test name",
        "max_players": 10,
        "creator": "Test creator",
        "players": [],
        "messages": []
    }
    tester.check(battle, exp_battle)
    tester.test("get_matches", [exp_battle])  # Матч уже создан
    # Должно успешно удалить матч
    tester.test("remove_match", True, exp_battle["name"])
    tester.test("get_matches", [])  # Матч должен быть удалён
    all_passed = tester.end() and all_passed

    # Аккаунты
    tester = Tester(logger, accounts.AccountManager, quiet)
    # 'Allowed name' состоит из разрешённых символов
    tester.test("check", True, "Allowed name")
    tester.test("check", False, "<name>")  # '<name>' содержит '<>'
    # Пустая строка не содержит запрещённых символов
    tester.test("check", True, "")
    tester.test("check", True, "Никнейм")  # Русские буквы разрешены
    # Остальных тестов AccountManager нет из-за изменения ими 'data.json'
    all_passed = tester.end() and all_passed

    return all_passed


if __name__ == "__main__":
    main()
