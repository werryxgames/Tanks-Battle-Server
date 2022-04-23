from tester import Tester
from sys import path

path.append("..")

from logger import Logger

import singleton
import mjson
import accounts


def main():
    # Тесты
    logger = Logger(Logger.LEVEL_DEBUG, Logger.LEVEL_NONE)

    # Синглтон
    tester = Tester(logger, singleton)
    tester.test("get_data", (None, None))  # Ещё не вызывалось 'set_data', должен вернуть (None, None)
    tester.test("set_data", None, "123", 456)  # Функция должна всегда возвращать None
    tester.test("get_data", ("123", 456))  # Функция должна вернуть то, что установила 'set_data'
    tester.test("set_data", None, "234")  # Функция должна работать, устанавливая только одно значение
    tester.test("set_data", None, logger="789")  # Функция должна работать с **kwargs
    tester.test("get_data", ("234", "789"))  # Проверка значений после 'set_data'
    tester.test("set_data", None, config=905)  # Функция должна работать с **kwargs
    tester.test("get_data", (905, "789"))  # Проверка значений после 'set_data'
    config = mjson.read("../config.json")  # Установка значений для корректной работы оставшихся тестов
    singleton.set_data(config)
    tester.test("get_matches", [])  # Матчи ещё не созданы
    tester.num += 1
    battle = tester.ret_value("add_match", "Test name", 10, "Test creator")
    tester.check_statement(battle.pop("map", False) is not False)  # В результате должен быть атрибут 'map'
    tester.num += 1
    exp_battle = {
        "name": "Test name",
        "max_players": 10,
        "creator": "Test creator",
        "players": 0
    }
    tester.check(battle, exp_battle)
    tester.test("get_matches", [exp_battle])  # Матч уже создан
    tester.test("remove_match", True, exp_battle["name"])  # Должно успешно удалить матч
    tester.test("get_matches", [])  # Матч должен быть удалён
    tester.end()

    # Аккаунты
    tester = Tester(logger, accounts.AccountManager)
    tester.test("check", True, "Allowed name")  # 'Allowed name' состоит из разрешённых символов
    tester.test("check", False, "<name>")  # '<name>' содержит '<>'
    tester.test("check", True, "")  # Пустая строка не содержит запрещённых символов
    tester.test("check", False, "Никнейм")  # Русские буквы не разрешены
    # Остальных тестов AccountManager нет из-за изменения ими 'data.json'
    tester.end()


if __name__ == "__main__":
    main()
