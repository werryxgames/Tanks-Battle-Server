from json import loads, dumps


def read(name):
	data = None

	with open(name, encoding="utf8") as f:
		data = loads(f.read())
	return data


def write(name, data):
	with open(name, "w", encoding="utf8") as f:
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
