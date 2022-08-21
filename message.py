"""Модуль с сообщениями."""


class GlobalMessage:
    """Класс глобального сообщения."""

    def __init__(self, type_, text):
        self.type = type_
        self.text = text

    def get(self):
        """Возвращает содержимое сообщения."""
        return (self.type, self.text)
