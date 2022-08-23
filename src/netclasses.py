"""Сетевые классы."""
from accounts import AccountManager
from singleton import get_data


class NetUser:
    """Класс пользователя."""

    def __init__(self, rudp):
        self.rudp = rudp

        self.login = None
        self.password = None
        self.account = None

        data = get_data()
        self.config = data[0]
        self.logger = data[1]

    def set_login_data(self, login, password):
        """Устанавливает данные для авторизации."""
        self.login = login
        self.password = password
        self.account = AccountManager.get_account(login)

        if self.account == AccountManager.FAILED_UNKNOWN or \
                self.account == AccountManager.FAILED_NOT_FOUND or \
                self.account["password"] != password:
            return False

        return True

    def refresh_account(self):
        """Перезагружает аккаунт и проверяет доступен ли он."""
        self.account = AccountManager.get_account(self.login)

        if self.account == AccountManager.FAILED_UNKNOWN or \
                self.account == AccountManager.FAILED_NOT_FOUND or \
                self.account["password"] != self.password:
            return False

        return True

    def send(self, *args, **kwargs):
        """Отправляет Reliable UDP пакет клиенту."""
        self.rudp.send(*args, **kwargs)
