"""Модуль с тестами к Tanks Battle Server."""
import singleton
import mjson
import accounts


def test_signleton():
    """Тесты синглтона."""
    # Ещё не вызывалось 'set_data', должен вернуть (None, None)
    assert singleton.get_data() == []
    # Функция должна всегда возвращать None
    assert singleton.set_data("123", 456, None) is None
    # Функция должна вернуть то, что установила 'set_data'
    assert singleton.get_data() == ["123", 456]
    # Функция должна работать, устанавливая только одно значение
    assert singleton.set_data("234") is None
    # Функция должна работать с **kwargs
    assert singleton.set_data(logger="789") is None
    # Проверка значений после 'set_data'
    assert singleton.get_data() == ["234", "789"]
    # Функция должна работать с **kwargs
    assert singleton.set_data(config=905) is None
    # Проверка значений после 'set_data'
    assert singleton.get_data() == [905, "789"]
    # Установка значений для корректной работы оставшихся тестов
    config = mjson.read("config.json")
    singleton.set_data(config)

    # Матчи ещё не созданы
    assert singleton.get_matches() == []
    battle = singleton.add_match("Test name", 10, "Test creator")
    # В результате должен быть атрибут 'map'
    assert battle.pop("map", False) is not False
    exp_battle = {
        "name": "Test name",
        "max_players": 10,
        "creator": "Test creator",
        "players": [],
        "messages": []
    }
    assert battle == exp_battle
    # Матч уже создан
    assert singleton.get_matches() == [exp_battle]
    # Должно успешно удалить матч
    assert singleton.remove_match(exp_battle["name"])
    assert singleton.get_matches() == []  # Матч должен быть удалён


def test_accounts():
    """Тесты модуля аккаунтов."""
    amanager = accounts.AccountManager
    # 'Allowed name' состоит из разрешённых символов
    assert amanager.check("Allowed name")
    assert not amanager.check("<name>")  # '<name>' содержит '<>'
    # Пустая строка не содержит запрещённых символов
    assert amanager.check("")
    assert amanager.check("Никнейм")  # Русские буквы разрешены
