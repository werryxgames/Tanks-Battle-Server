"""Network classes."""
from accounts import AccountManager
from singleton import get_data


class NetUser:
    """Class for user."""

    def __init__(self, rudp):
        """User initializarion."""
        self.rudp = rudp

        self.login = None
        self.password = None
        self.account = None

        data = get_data()
        self.config = data[0]
        self.logger = data[1]

    def set_login_data(self, login, password):
        """Sets data for authorization."""
        self.login = login
        self.password = password
        self.account = AccountManager.get_account(login)

        if self.account == AccountManager.FAILED_UNKNOWN or \
                self.account == AccountManager.FAILED_NOT_FOUND or \
                self.account["password"] != password:
            return False

        return True

    def refresh_account(self):
        """Refreshes account and checks is it available."""
        self.account = AccountManager.get_account(self.login)

        if self.account == AccountManager.FAILED_UNKNOWN or \
                self.account == AccountManager.FAILED_NOT_FOUND or \
                self.account["password"] != self.password:
            return False

        return True

    def send(self, *args, **kwargs):
        """Sends Reliable UDP packet to client."""
        self.rudp.send(*args, **kwargs)
