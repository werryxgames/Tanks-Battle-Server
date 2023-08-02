"""JSON module."""
from json import dumps
from json import loads

from absolute import to_absolute


def read(name, default=None):
    """Returns data from *.json file."""
    data = None

    try:
        with open(to_absolute(name), encoding="utf8") as file:
            data = loads(file.read())
    except FileNotFoundError:
        return default

    return data


def write(name, data):
    """Writes data to *.json file."""
    with open(to_absolute(name), "w", encoding="utf8") as file:
        file.write(dumps(data, indent=4, ensure_ascii=False))

    return True


def append(name, key=None, value=None, default=None):
    """Adds value to key in file name."""
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
