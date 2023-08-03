"""Accounts module."""
from datetime import datetime
from threading import Thread

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from mjson import append
from mjson import read
from mjson import write
from singleton import get_data
from serializer import ByteBuffer


class Hasher:
    """Class for password hashing."""

    def __init__(self):
        """Password hasher initialization."""
        self.phasher = PasswordHasher()

    @staticmethod
    def rehash_password(nick, new_hash):
        """Sets new hash in accounts.json."""
        return AccountManager.set_account(nick, "password", new_hash)

    def hash(self, password, nick):
        """Hashes password."""
        result = self.phasher.hash(password + nick)
        return result

    def verify(self, hash_, password, nick):
        """Checks if hash_ is hash of data."""
        try:
            self.phasher.verify(hash_, password + nick)
        except VerifyMismatchError:
            return False

        if self.phasher.check_needs_rehash(hash_):
            new_hash = self.hash(password, nick)
            self.rehash_password(nick, new_hash)

        return True


hasher = Hasher()
queued_logins = []


class AccountManager:
    """Manages accounts."""

    SUCCESSFUL = 0
    FAILED_NICK_LENGTH = 1
    FAILED_UNKNOWN = 2
    FAILED_PASSWORD_LENGTH = 3
    FAILED_NICK_ALREADY_USED = 4
    FAILED_UNSAFE_CHARACTERS = 5
    LOGGED_IN = 6
    FAILED_NOT_FOUND = 7
    FAILED_PASSWORD_NOT_MATCH = 7
    FAILED_BAN = 8
    FAILED_CONSOLE = 11
    FAILED_NOT_EXISTS = 11
    DEFAULT_ALLOWED = "qwertyuiopasdfghjklzxcvbnm1234567890_ -=+*/[]:;.,\\|&%\
#@!$^()йцукенгшщзхъфывапролджэячсмитьбюёў"

    @staticmethod
    def check(string, allowed=DEFAULT_ALLOWED):
        """Checks if string consists only of allowed."""
        return set(string.lower()) <= set(allowed)

    @staticmethod
    def get_account_(nick, data):
        """Returns account with login nick from data."""
        for account in data:
            if account["nick"] == nick:
                return account

        return AccountManager.FAILED_NOT_FOUND

    @staticmethod
    def get_account(nick):
        """Returns account with login nick."""
        data = read("accounts.json", [])

        return AccountManager.get_account_(nick, data)

    @staticmethod
    def del_account_key_(nick, key, data):
        """Deleted key from account with login nick from data."""
        acc = AccountManager.get_account_(nick, data)

        if acc == AccountManager.FAILED_NOT_FOUND:
            return acc

        try:
            del data[data.index(acc)][key]

            return data
        except KeyError:
            return AccountManager.FAILED_NOT_EXISTS

    @staticmethod
    def call_method(method, *args):
        """Calls method."""
        data = read("accounts.json", [])
        result = method(*args, data)

        if isinstance(result, int):
            return result

        if write("accounts.json", result):
            return AccountManager.SUCCESSFUL

        return AccountManager.FAILED_UNKNOWN

    @staticmethod
    def del_account_key(nick, key):
        """Deletes key from account with login nick."""
        return AccountManager.call_method(
            AccountManager.del_account_key_,
            nick,
            key
        )

    @staticmethod
    def del_account_(nick, data):
        """Deletes account with login nick from data."""
        acc = AccountManager.get_account_(nick, data)

        if acc == AccountManager.FAILED_NOT_FOUND:
            return acc

        del data[data.index(acc)]

        if write("accounts.json", data):
            return AccountManager.SUCCESSFUL

        return AccountManager.FAILED_UNKNOWN

    @staticmethod
    def del_account(nick):
        """Deletes account with login nick."""
        return AccountManager.call_method(
            AccountManager.del_account_,
            nick
        )

    @staticmethod
    def set_account_(nick, key, value, data):
        """Sets value of key to value for account with login nick."""
        acc = AccountManager.get_account_(nick, data)

        if acc == AccountManager.FAILED_NOT_FOUND:
            return acc

        try:
            data[data.index(acc)][key] = value
        except (ValueError, IndexError):
            data[key] = [value]

        return data

    @staticmethod
    def set_account(nick, key, value):
        """Sets value for account."""
        return AccountManager.call_method(
            AccountManager.set_account_,
            nick,
            key,
            value
        )

    @staticmethod
    def check_login_data(data, lenfail, minlen=3, maxlen=12):
        """Checks login data without match check."""
        if not isinstance(data, str):
            return AccountManager.FAILED_UNKNOWN

        data = data.strip()

        if len(data) < minlen or (maxlen != -1 and len(data) > maxlen):
            return lenfail

        if not AccountManager.check(data):
            return AccountManager.FAILED_UNSAFE_CHARACTERS

        return AccountManager.SUCCESSFUL

    @staticmethod
    def get_ban_status_(data, account):
        """Returns ban (block) status in account."""
        if "ban" in account:
            aban = account["ban"]

            if aban[0] != -1 and datetime.today().timestamp() \
                    > aban[0]:
                del data[data.index(account)]["ban"]
                return AccountManager.SUCCESSFUL

            if len(aban) > 1:
                return [
                    AccountManager.FAILED_BAN,
                    ByteBuffer(2 + 4 + len(aban[1].encode("UTF-8")) + 1)
                    .put_u16(AccountManager.FAILED_BAN)
                    .put_u32(aban[0])
                    .put_string(aban[1])
                    .to_bytes()
                ]

            return [
                AccountManager.FAILED_BAN,
                ByteBuffer(2 + 4)
                .put_u16(AccountManager.FAILED_BAN)
                .put_u32(aban[0])
                .to_bytes()
            ]

        return AccountManager.SUCCESSFUL

    @staticmethod
    def get_ban_status(data, account):
        """Returns ban (block) status in account."""
        result = AccountManager.get_ban_status_(data, account)

        if isinstance(result, int):
            return result

        write("accounts.json", data)
        return AccountManager.SUCCESSFUL

    @staticmethod
    def login_account(nick, password, client):
        """Checks is login data correct and removes nick from list."""
        AccountManager.login_account_(nick, password, client)
        queued_logins.remove(nick)

    @staticmethod
    def login_account_(nick, password, client):
        """Checks is login data correct synchronously."""
        nick_check = AccountManager.check_login_data(
            nick,
            AccountManager.FAILED_NICK_LENGTH
        )

        if nick_check != AccountManager.SUCCESSFUL:
            client.send(ByteBuffer(2).put_u16(nick_check).to_bytes())
            return

        pass_check = AccountManager.check_login_data(
            password,
            AccountManager.FAILED_PASSWORD_LENGTH,
            6,
            -1
        )

        if pass_check != AccountManager.SUCCESSFUL:
            client.send(ByteBuffer(2).put_u16(pass_check).to_bytes())
            return

        nick = nick.strip()
        password = password.strip()

        data = read("accounts.json", [])

        for account in data:
            if account["nick"] == nick:
                if hasher.verify(account["password"], password, nick):
                    if "console" in account:
                        client.send(
                            ByteBuffer(
                                2 + len(nick.encode("UTF-8")) + 1 + len(
                                    password.encode("UTF-8")
                                ) + 1
                            )
                            .put_u16(AccountManager.FAILED_CONSOLE)
                            .put_string(nick)
                            .put_string(password)
                            .to_bytes()
                        )
                        client.console = client.CONSOLE(
                            client.sock,
                            client.addr,
                            client.rudp
                        )
                        return

                    ban_status = AccountManager.get_ban_status(data, account)

                    if isinstance(
                        ban_status,
                        list
                    ) and ban_status[0] == AccountManager.FAILED_BAN:
                        client.send(ban_status[1])
                        return

                    if ban_status == AccountManager.SUCCESSFUL:
                        client.send(
                            ByteBuffer(
                                2 + len(nick.encode("UTF-8")) + 1 + len(
                                    password.encode("UTF-8")
                                ) + 1
                            )
                            .put_u16(AccountManager.LOGGED_IN)
                            .put_string(nick)
                            .put_string(password)
                            .to_bytes()
                        )
                        client.client.set_login_data(nick, password)
                        client.send_client = True
                        return

                    client.send(ByteBuffer(2).put_u16(ban_status).to_bytes())
                    return

                client.send(
                    ByteBuffer(2)
                    .put_u16(AccountManager.FAILED_PASSWORD_NOT_MATCH)
                    .to_bytes()
                )
                return

        client.send(
            ByteBuffer(2).put_u16(AccountManager.FAILED_NOT_FOUND).to_bytes()
        )

    @staticmethod
    def login_account_async(nick, password, client):
        """Chekcs is login data correct asynchronously."""
        if nick in queued_logins:
            return False

        queued_logins.append(nick)
        thread = Thread(
            target=AccountManager.login_account,
            args=(nick, password, client)
        )
        thread.start()
        return True

    @staticmethod
    def add_account(nick, password, client):
        """Creates new account and removes nick from list."""
        AccountManager.add_account_(nick, password, client)
        queued_logins.remove(nick)

    @staticmethod
    def add_account_(nick, password, client):
        """Creates new account synchronously."""
        nick_check = AccountManager.check_login_data(
            nick,
            AccountManager.FAILED_NICK_LENGTH
        )

        if nick_check != AccountManager.SUCCESSFUL:
            client.send(ByteBuffer(2).put_u16(nick_check).to_bytes())
            return

        pass_check = AccountManager.check_login_data(
            password,
            AccountManager.FAILED_PASSWORD_LENGTH,
            6,
            -1
        )

        if pass_check != AccountManager.SUCCESSFUL:
            client.send(ByteBuffer(2).put_u16(pass_check).to_bytes())
            return

        nick = nick.strip()
        password = password.strip()

        data = read("accounts.json", [])

        for account in data:
            if account["nick"] == nick:
                client.send(
                    ByteBuffer(2)
                    .put_u16(AccountManager.FAILED_NICK_ALREADY_USED)
                    .to_bytes()
                )
                return

        hashed_password = hasher.hash(password, nick)

        acc = {
            "nick": nick,
            "password": hashed_password,
            "xp": 0,
            "crystals": 0,
            "tanks": [0],
            "selected_tank": 0,
            "settings": get_data()[0]["default_settings"]
        }

        if append("accounts.json", None, acc, []):
            client.send(
                ByteBuffer(
                    2 + len(nick.encode("UTF-8")) + 1 + len(
                        password.encode("UTF-8")
                    ) + 1
                )
                .put_u16(AccountManager.SUCCESSFUL)
                .put_string(nick)
                .put_string(password)
                .to_bytes()
            )
            client.client.set_login_data(nick, password)
            client.send_client = True
            return

        client.send(
            ByteBuffer(2)
            .put_u16(AccountManager.FAILED_UNKNOWN)
            .to_bytes()
        )
        return

    @staticmethod
    def add_account_async(nick, password, client):
        """Creates new account asynchronously."""
        if nick in queued_logins:
            return False

        queued_logins.append(nick)
        thread = Thread(
            target=AccountManager.add_account,
            args=(nick, password, client)
        )
        thread.start()
        return True
