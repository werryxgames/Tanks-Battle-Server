from struct import pack


class ByteTranslatorException(Exception):
    """Базовое исключение для ByteTranslator."""


class ByteTranslator:
    """Класс для преобразования байтов в данные и наоборот."""

    COM_BYTE_TRANSLATIONS = {
        "something_wrong": (0, 1),
        "register": (0, 2),
        "login": (0, 3),
        "get_account_data": (0, 4),
        "client_disconnected": (0, 5),
        "console_command": (0, 6)
    }
    DATATYPES = {
        int: 1,
        str: 2,
        float: 3,
        list: 4,
        tuple: 4,
        dict: 5,
        type(None): 6,
        bool: 7
    }

    @classmethod
    def get_com_bytes(cls, com):
        """Возвращает bytearray из com-строки."""
        try:
            return bytearray(cls.COM_BYTE_TRANSLATIONS[com])
        except KeyError:
            pass

        raise ByteTranslatorException("Указанная com-строка не найдена")

    @classmethod
    def get_datatype(cls, data):
        """Возвращает тип данных как число."""
        try:
            return cls.DATATYPES[type(data)]
        except KeyError:
            pass

        raise ByteTranslatorException("Тип указанных данных не найден")

    @staticmethod
    def bappend(original_barr, appending_barr):
        """Добавляет appending_barr к original_barr."""
        for byte in appending_barr:
            original_barr.append(byte)

    @staticmethod
    def str_to_bytes(data):
        """Преобразует строку в байты."""
        barr = bytearray()

        for byte in data.encode("utf8"):
            barr.append(byte)

        barr.append(0)
        return barr

    @staticmethod
    def int_to_bytes(data):
        """Преобразует целое число в байты."""
        barr = bytearray()
        last_length = -1

        for length in range(1, 257):
            try:
                bytes_ = int.to_bytes(data, length, "big", signed=True)
                last_length = length - 1
                break
            except OverflowError:
                continue

        barr.append(last_length)
        ByteTranslator.bappend(barr, bytes_)
        return barr

    @staticmethod
    def float_to_bytes(data):
        """Преобразует дробное число в байты."""
        barr = bytearray()
        ByteTranslator.bappend(barr, pack("f", data))
        return barr

    @staticmethod
    def array_to_bytes(data):
        """Преобразует массив в байты."""
        barr = bytearray()

        try:
            barr.append(len(data))
            ByteTranslator.bappend(barr, ByteTranslator.to_bytes(data))
            return barr
        except ValueError:
            pass

        raise ByteTranslatorException("Длина массива больше максимальной")

    @staticmethod
    def dict_to_bytes(data):
        """Преобразует словарь в байты."""
        barr = bytearray()
        dictval = []

        for key, value in data.items():
            dictval.append((key, value))

        try:
            barr.append(len(dictval))

            for byte in ByteTranslator.to_bytes(dictval):
                barr.append(byte)

            return barr
        except ValueError:
            pass

        raise ByteTranslatorException("Длина словаря больше максимальной")

    @staticmethod
    def bool_to_bytes(data):
        """Преобразует булевое значение в байты."""
        return bytearray([1]) if data else bytearray([0])

    @staticmethod
    def to_bytes(data):
        """Преобразует data в байты."""
        barr = bytearray()

        for arg in data:
            dtype = ByteTranslator.get_datatype(arg)
            barr.append(dtype)

            if dtype == 1:
                ByteTranslator.bappend(
                    barr,
                    ByteTranslator.int_to_bytes(arg)
                )
            elif dtype == 2:
                ByteTranslator.bappend(
                    barr,
                    ByteTranslator.str_to_bytes(arg)
                )
            elif dtype == 3:
                ByteTranslator.bappend(
                    barr,
                    ByteTranslator.float_to_bytes(arg)
                )
            elif dtype == 4:
                ByteTranslator.bappend(
                    barr,
                    ByteTranslator.array_to_bytes(arg)
                )
            elif dtype == 5:
                ByteTranslator.bappend(
                    barr,
                    ByteTranslator.dict_to_bytes(arg)
                )
            elif dtype == 7:
                barr.append(1 if arg else 0)

        return barr

    @staticmethod
    def to_data(bytes_):
        """Преобразует bytes_ в данные."""
