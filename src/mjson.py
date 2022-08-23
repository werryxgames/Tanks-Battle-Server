"""Модуль JSON."""
from json import dumps
from json import loads

from absolute import to_absolute


def read(name, default=None):
    """Возвращает данные из *.json файла."""
    data = None

    try:
        with open(to_absolute(name), encoding="utf8") as file:
            data = loads(file.read())
    except FileNotFoundError:
        return default

    return data


def write(name, data):
    """Записывает данные в *.json файл."""
    with open(to_absolute(name), "w", encoding="utf8") as file:
        file.write(dumps(data, indent=4, ensure_ascii=False))

    return True


def append(name, key=None, value=None, default=None):
    """Добавляет value к key файла name."""
    data = read(name, default)

    if data is None:
        return None

    if key is None:
        try:
            data.append(value)
        except (ValueError, IndexError):
            data = [value]
    else:
        try:
            data[key].append(value)
        except (ValueError, IndexError):
            data[key] = [value]

    return write(name, data)
