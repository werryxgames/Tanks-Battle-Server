"""Модуль консоли."""
from datetime import datetime
from json import dumps
from shlex import split as spl

from accounts import AccountManager
from message import GlobalMessage
from singleton import get_data
from singleton import get_matches


class ConsoleExecutor:
    """Выполняет консольные команды."""

    def __init__(
        self,
        sock=None,
        addr=None,
        config=None,
        logger=None,
        win=None,
        rudp=None
    ):
        """Инициализация исполнителя консольных команд."""
        self.sock = sock
        self.addr = addr
        self.rudp = rudp
        self.config = config
        self.logger = logger
        self.win = win
        self.vars = {}

    def send(self, message):
        """Отправляет Reliable UDP сообщение клиенту."""
        if self.sock is not None:
            self.rudp.send(["console_result", message])

        if self.logger is not None:
            if self.addr is not None:
                self.logger.debug(f"Результат команды отправлен клиенту '\
{self.addr[0]}:{self.addr[1]}':", message)
        elif self.sock is None and self.win is not None and \
                self.win.state == self.win.STATE_CONSOLE:
            self.win.elements[2].configure(state="normal")
            self.win.elements[2].insert("end", str(message) + "\n")
            self.win.elements[2].configure(state="disabled")

    @staticmethod
    def get_value(value):
        """Возвращает значение из строки."""
        if value[0] == "\\":
            return value[1:]

        try:
            return int(value)
        except ValueError:
            return value

    @staticmethod
    def execute_ban_player(args):
        """Выполняет команду блокировки игрока."""
        nick = args[1]

        try:
            if args[2] == "-1":
                tstamp = -1
            else:
                time = args[2].split(".")
                tstamp = datetime(
                    int(time[2]),
                    int(time[1]),
                    int(time[0])
                ).timestamp()

            reason = None

            if len(args) > 3:
                reason = " ".join(args[3:])

            status = AccountManager.set_account(
                nick,
                "ban",
                [tstamp, reason]
            )

            if status == AccountManager.SUCCESSFUL:
                string = f"Аккаунт '{nick}' заблокирован "

                if tstamp == -1:
                    string += "навсегда"
                else:
                    string += "до " + args[2]

                string += ", причина"

                if reason is None:
                    string += " не указана"
                else:
                    string += ": '" + reason + "'"

                return string

            if status == AccountManager.FAILED_NOT_FOUND:
                return "Аккаунт не найден"

            return "Не удалось выполнить команду"
        except (ValueError, IndexError):
            return "Неверный синтаксис команды: 'account <никнейм> \
ban (<день>.<месяц>.<год> | -1) [причина]'"

    @staticmethod
    def execute_account_setget(args):
        """Выполняет установку/получение значения аккаунта."""
        nick = args[0]
        act = args[1]

        if act == "set":
            if len(args) <= 3:
                return "Ошибка команды"

            key = args[2]
            val = ConsoleExecutor.get_value(args[3])

            status = AccountManager.set_account(nick, key, val)

            if status == AccountManager.SUCCESSFUL:
                string = f"Установлено значение '{key}' в "
                string += str(val) if isinstance(val, int) else f"'{val}'"
                string += f" для аккаунта '{nick}'"
                return string

            if status == AccountManager.FAILED_NOT_FOUND:
                return "Аккаунт не найден"

            return "Не удалось выполнить команду"

        if act == "get":
            status = AccountManager.get_account(nick)

            if status == AccountManager.FAILED_NOT_FOUND:
                return "Аккаунт не найден"

            if status == AccountManager.FAILED_UNKNOWN:
                return "Не удалось выполнить команду"

            return status[args[2]] if len(args) > 2 else status

        return None

    @staticmethod
    def execute_account_del(args):
        """Удаляет ключ аккаунта."""
        if len(args) <= 2:
            return "Ошибка команды"

        nick = args[0]
        key = args[2]
        status = AccountManager.del_account_key(nick, key)

        if status == AccountManager.SUCCESSFUL:
            return f"Удален ключ '{key}' для аккаунта '{nick}'"

        if status == AccountManager.FAILED_NOT_FOUND:
            return "Аккаунт не найден"

        if status == AccountManager.FAILED_UNKNOWN:
            return "Не удалось выполнить команду"

        if status == AccountManager.FAILED_NOT_EXISTS:
            return f"Ключ '{key}' не найден в аккаунте '{nick}'"

        return "Не удалось выполнить команду"

    @staticmethod
    def execute_unban_player(args):
        """Разблокирует аккаунт игрока."""
        nick = args[0]
        status = AccountManager.del_account_key(nick, "ban")

        if status == AccountManager.SUCCESSFUL:
            return f"Аккаунт '{nick}' разблокирован"

        if status == AccountManager.FAILED_NOT_EXISTS:
            return f"Аккаунт '{nick}' ещё не заблокирован"

        if status == AccountManager.FAILED_NOT_FOUND:
            return "Аккаунт не найден"

        return "Не удалось выполнить команду"

    @staticmethod
    def execute_remove_account(args):
        """Удаляет аккаунт."""
        if len(args) != 2:
            return "Команда 'account <никнейм> remove' не принимает \
аргументов. Возможно вы имели ввиду 'account <никнейм> del'"

        nick = args[0]
        status = AccountManager.del_account(nick)

        if status == AccountManager.SUCCESSFUL:
            return f"Аккаунт '{nick}' удалён"

        if status == AccountManager.FAILED_NOT_FOUND:
            return "Аккаунт не найден"

        return "Не удалось выполнить команду"

    @staticmethod
    def execute_account(args):
        """Выполняет команду аккаунта."""
        if len(args) < 2:
            return "Ошибка команды"

        act = args[1]

        sgstatus = ConsoleExecutor.execute_account_setget(args)

        if sgstatus is not None:
            return sgstatus

        if act == "del":
            return ConsoleExecutor.execute_account_del(args)

        if act == "ban":
            return ConsoleExecutor.execute_ban_player(args)

        if act == "unban":
            return ConsoleExecutor.execute_unban_player(args)

        if act == "remove":
            return ConsoleExecutor.execute_remove_account(args)

        return "Неверный синтаксис команды"

    @staticmethod
    def execute_player_battle(args, battle, battles):
        """Выполняет команду над битвой игрока."""
        if len(args) < 3:
            return "Ошибка команды"

        act2 = args[2]

        if act2 == "players":
            pls = []

            for pl in battle["players"]:
                pls.append(pl.nick)

            return pls

        if act2 == "end":
            del battles[battles.index(battle)]
            return "Матч завершён"

        return "Неверный синтаксис команды"

    @staticmethod
    def execute_player(args):
        """Выполняет команду игрока."""
        if len(args) < 2:
            return "Ошибка команды"

        nick = args[0]
        act = args[1]

        battle = None
        player = None
        battles = get_matches()

        for i in battles:
            for pl in i["players"]:
                if pl.nick == nick:
                    battle = i
                    player = pl
                    break

            if player is not None:
                break

        if player is None:
            return "Игрок не найден, или не в матче сейчас"

        if act == "kick":
            battle["messages"].append(GlobalMessage("player_leave", nick))
            return "Игрок отключён от матча"

        if act == "battle":
            return ConsoleExecutor.execute_player_battle(args, battle, battles)

        return "Неверный синтаксис команды"

    @staticmethod
    def execute(com, args):
        """Выполняет команду com с аргументами args."""
        if com == "account":
            return ConsoleExecutor.execute_account(args)

        if com == "player":
            return ConsoleExecutor.execute_player(args)

        return "Команда не найдена"

    def execute_text(self, text, main=True):
        """Выполняет команду как текст."""
        try:
            splt = spl(text)

            if "<" in splt:
                index = splt.index("<")
                start = splt[0:index]
                end = splt[index + 1:]
                arg = str(self.execute_text(" ".join(end), False))
                st = start[1:]

                if "$" in st:
                    st[st.index("$")] = arg
                else:
                    st.append(arg)

                res = self.execute(start[0], st)

                if main:
                    self.send(res)
                else:
                    return res
            else:
                res = self.execute(splt[0], splt[1:])

                if main:
                    self.send(res)
                else:
                    return res
        except IndexError:
            pass

        return None


class Console:
    """Класс консоли команд."""

    def __init__(self, sock, addr, rudp):
        """Инициализация консоли команд."""
        self.sock = sock
        self.addr = addr
        self.rudp = rudp

        data = get_data()
        self.config = data[0]
        self.logger = data[1]

        self.cexr = ConsoleExecutor(
            self.sock,
            self.addr,
            self.config,
            self.logger,
            rudp=self.rudp
        )

    def send(self, message):
        """Отправляет сообщение клиенту."""
        self.sock.sendto(dumps(message).encode("utf8"), self.addr)
        self.logger.debug(
            f"Сообщение отправлено клиенту '{self.addr[0]}:{self.addr[1]}':",
            message
        )

    def close(self):
        """Закрывает соединение с клиентом."""
        try:
            self.send(["something_wrong"])
            self.logger.info(f"Клиент '{self.addr[0]}:{self.addr[1]}' вызвал \
ошибку на сервере")
        except OSError:
            pass

    def receive(self, jdt):
        """Обрабатывает данные, полученные от клиента."""
        try:
            com = jdt[0]
            args = jdt[1:]

            if com == "console_command":
                self.cexr.execute_text(" ".join(args))

        except BaseException:
            self.logger.log_error_data()
            self.close()

            return
