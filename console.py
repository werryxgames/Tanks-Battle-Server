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
    def execute(com, args):
        """Выполняет команду com с аргументами args."""
        if com == "account":
            if len(args) < 2:
                return "Ошибка команды"

            nick = args[0]
            act = args[1]

            if act == "set":
                if len(args) <= 3:
                    return "Ошибка команды"

                key = args[2]
                val = args[3]

                if val[0] == "\\":
                    val = val[1:]
                else:
                    try:
                        val = int(val)
                    except ValueError:
                        pass

                status = AccountManager.set_account(nick, key, val)

                if status == AccountManager.SUCCESSFUL:
                    s = f"Установлено значение '{key}' в "
                    if isinstance(val, int):
                        s += str(val)
                    else:
                        s += f"'{val}'"
                    s += f" для аккаунта '{nick}'"
                    return s

                if status == AccountManager.FAILED_NOT_FOUND:
                    return "Аккаунт не найден"

                if status == AccountManager.FAILED_UNKNOWN:
                    return "Не удалось выполнить команду"
            elif act == "get":
                if len(args) > 2:
                    key = args[2]
                else:
                    key = None

                status = AccountManager.get_account(nick)

                if status == AccountManager.FAILED_NOT_FOUND:
                    return "Аккаунт не найден"

                if status == AccountManager.FAILED_UNKNOWN:
                    return "Не удалось выполнить команду"

                if key is None:
                    return status

                return status[key]
            elif act == "del":
                if len(args) <= 2:
                    return "Ошибка команды"

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
            elif act == "ban":
                try:
                    if args[2] == "-1":
                        ts = -1
                    else:
                        time = args[2].split(".")
                        ts = datetime(
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
                        [ts, reason]
                    )

                    if status == AccountManager.SUCCESSFUL:
                        s = f"Аккаунт '{nick}' заблокирован "
                        if ts == -1:
                            s += "навсегда"
                        else:
                            s += "до " + args[2]
                        s += ", причина"
                        if reason is None:
                            s += " не указана"
                        else:
                            s += ": '" + reason + "'"
                        return s

                    if status == AccountManager.FAILED_NOT_FOUND:
                        return "Аккаунт не найден"

                    if status == AccountManager.FAILED_UNKNOWN:
                        return "Не удалось выполнить команду"
                except (ValueError, IndexError):
                    return "Неверный синтаксис команды: 'account <никнейм> \
ban (<день>.<месяц>.<год> | -1) [причина]'"
            elif act == "unban":
                status = AccountManager.del_account_key(nick, "ban")

                if status == AccountManager.SUCCESSFUL:
                    return f"Аккаунт '{nick}' разблокирован"

                if status == AccountManager.FAILED_NOT_EXISTS:
                    return f"Аккаунт '{nick}' ещё не заблокирован"

                if status == AccountManager.FAILED_NOT_FOUND:
                    return "Аккаунт не найден"

                if status == AccountManager.FAILED_UNKNOWN:
                    return "Не удалось выполнить команду"
            elif act == "remove":
                if len(args) == 2:
                    status = AccountManager.del_account(nick)

                    if status == AccountManager.SUCCESSFUL:
                        return f"Аккаунт '{nick}' удалён"

                    if status == AccountManager.FAILED_NOT_FOUND:
                        return "Аккаунт не найден"

                    if status == AccountManager.FAILED_UNKNOWN:
                        return "Не удалось выполнить команду"
                else:
                    return "Команда 'account <никнейм> remove' не принимает \
аргументов. Возможно вы имели ввиду 'account <никнейм> del'"
        elif com == "player":
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
        """Обрабатывает данные, полученные от клиента"""
        try:
            com = jdt[0]
            args = jdt[1:]

            if com == "console_command":
                self.cexr.execute_text(" ".join(args))

        except BaseException:
            self.logger.log_error_data()
            self.close()

            return
