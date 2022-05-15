from json import loads, dumps
from absolute import to_absolute


def read(name):
    data = None

    with open(to_absolute(name), encoding="utf8") as f:
        data = loads(f.read())

    return data


def write(name, data):
    with open(to_absolute(name), "w", encoding="utf8") as f:
        f.write(dumps(data, indent=4, ensure_ascii=False))

    return True


def append(name, key, value):
    data = read(name)

    if data is None:
        return None

    try:
        data[key].append(value)
    except (ValueError, IndexError):
        data[key] = [value]

    return write(name, data)
