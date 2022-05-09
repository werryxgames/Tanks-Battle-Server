from json import loads, dumps
from datetime import datetime
from shlex import split as spl
from singleton import get_data, get_matches
from message import GlobalMessage
from accounts import AccountManager


class ConsoleExecutor:
    SUCCESSFUL = 0
    FAILED = 1
    USE_MSG = 2

    def __init__(self, sock, addr, config, logger):
        self.sock = sock
        self.addr = addr
        self.config = config
        self.logger = logger
        self.vars = {}

    def send(self, message):
        self.sock.sendto(dumps(["console_result", message]).encode("utf8"), self.addr)
        self.logger.debug(f"Результат команды отправлен клиенту '{self.addr[0]}:{self.addr[1]}':", message)

    def send_part(self, message):
        self.sock.sendto(dumps(["console_result_part", message]).encode("utf8"), self.addr)
        self.logger.debug(f"Часть результата команды отправлена клиенту '{self.addr[0]}:{self.addr[1]}':", message)

    def execute(self, com, args):
        if com[0] == "$":
            try:
                if com[1] == "!":
                    var = self.vars[com[2:]]
                    return self.USE_MSG, var[0]
                elif com[1] == "@":
                    var = self.vars[com[2:]]
                    return self.USE_MSG, var[1]
                else:
                    var = self.vars[com[1:]]
                    if var[0] == self.USE_MSG:
                        return self.USE_MSG, var[1]
                    else:
                        return self.USE_MSG, var[0]
            except KeyError:
                return self.FAILED, f"Переменная '{com[1:]}' не найдена"
        elif com == "account":
            if len(args) < 2:
                return self.FAILED, "Ошибка команды"

            nick = args[0]
            act = args[1]

            if act == "set":
                key = args[2]
                val = loads(args[3])
                status = AccountManager.set_account(nick, key, val)
                if status == AccountManager.SUCCESSFUL:
                    return self.SUCCESSFUL, f"Установлено значение '{key}' в {val} для аккаунта '{nick}'"
                elif status == AccountManager.FAILED_NOT_FOUND:
                    return self.FAILED, f"Аккаунт не найден"
                elif status == AccountManager.FAILED_UNKNOWN:
                    return self.FAILED, f"Не удалось выполнить команду"
            elif act == "get":
                if len(args) > 2:
                    key = args[2]
                else:
                    key = None
                status = AccountManager.get_account(nick)
                if status == AccountManager.FAILED_NOT_FOUND:
                    return self.FAILED, f"Аккаунт не найден"
                elif status == AccountManager.FAILED_UNKNOWN:
                    return self.FAILED, f"Не удалось выполнить команду"
                else:
                    if key is None:
                        return self.SUCCESSFUL, status
                    else:
                        return self.SUCCESSFUL, status[key]
            elif act == "del":
                key = args[2]
                status = AccountManager.del_account_key(nick, key)
                if status == AccountManager.SUCCESSFUL:
                    return self.SUCCESSFUL, f"Удален ключ '{key}' для аккаунта '{nick}'"
                elif status == AccountManager.FAILED_NOT_FOUND:
                    return self.FAILED, f"Аккаунт не найден"
                elif status == AccountManager.FAILED_UNKNOWN:
                    return self.FAILED, f"Не удалось выполнить команду"
                elif status == AccountManager.FAILED_NOT_EXISTS:
                    return self.FAILED, f"Ключ '{key}' не найден в аккаунте '{nick}'"
            elif act == "ban":
                try:
                    if args[2] == "-1":
                        ts = -1
                    else:
                        time = args[2].split(".")
                        ts = datetime(int(time[2]), int(time[1]), int(time[0])).timestamp()
                    reason = None
                    if len(args) > 3:
                        reason = " ".join(args[3:])

                    status = AccountManager.set_account(nick, "ban", [ts, reason])
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
                        return self.SUCCESSFUL, s
                    elif status == AccountManager.FAILED_NOT_FOUND:
                        return self.FAILED, f"Аккаунт не найден"
                    elif status == AccountManager.FAILED_UNKNOWN:
                        return self.FAILED, f"Не удалось выполнить команду"
                except (ValueError, IndexError):
                    return self.FAILED, "Неверный синтаксис команды: 'account <никнейм> ban (<день>.<месяц>.<год> | -1) [причина]'"
            elif act == "unban":
                status = AccountManager.del_account_key(nick, "ban")
                if status == AccountManager.SUCCESSFUL:
                    return self.SUCCESSFUL, f"Аккаунт '{nick}' разблокирован"
                elif status == AccountManager.FAILED_NOT_EXISTS:
                    return self.FAILED, f"Аккаунт '{nick}' ещё не заблокирован"
                elif status == AccountManager.FAILED_NOT_FOUND:
                    return self.FAILED, f"Аккаунт не найден"
                elif status == AccountManager.FAILED_UNKNOWN:
                    return self.FAILED, f"Не удалось выполнить команду"
            elif act == "remove":
                if len(args) == 2:
                    status = AccountManager.del_account(nick)
                    if status == AccountManager.SUCCESSFUL:
                        return self.SUCCESSFUL, f"Аккаунт '{nick}' удалён"
                    elif status == AccountManager.FAILED_NOT_FOUND:
                        return self.FAILED, f"Аккаунт не найден"
                    elif status == AccountManager.FAILED_UNKNOWN:
                        return self.FAILED, f"Не удалось выполнить команду"
                else:
                    return self.FAILED, "Команда 'account <никнейм> remove' не принимает аргументов. Возможно вы имели ввиду 'account <никнейм> del'"
            else:
                return self.FAILED, "Команда не найдена"
        elif com == "player":
            if len(args) < 2:
                return self.FAILED, "Ошибка команды"

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
                return self.FAILED, "Игрок не найден, или не в матче сейчас"

            if act == "kick":
                battle["messages"].append(GlobalMessage("player_leave", nick))
                return self.SUCCESSFUL, "Игрок отключён от матча"
            elif act == "battle":
                if len(args) < 3:
                    return self.FAILED, "Ошибка команды"

                act2 = args[2]
                if act2 == "players":
                    pls = []
                    for pl in battle["players"]:
                        pls.append(pl.nick)
                    return self.SUCCESSFUL, pls
                elif act2 == "end":
                    del battles[battles.index(battle)]
                    return self.SUCCESSFUL, "Матч завершён"
                else:
                    return self.FAILED, "Команда не найдена"
            else:
                return self.FAILED, "Команда не найдена"
        else:
            return self.FAILED, "Команда не найдена"

    def execute_text(self, text):
        splt = spl(text)
        buf = None
        msg = None
        if len(splt) > 0:
            command = []
            wait = "command"
            buffer = ""
            for i in splt:
                if i == ">":
                    wait = "redirect"
                elif wait == "redirect":
                    if len(command) > 0:
                        buf, msg = self.execute(command[0], command[1:])
                        if i[0] == "$":
                            self.vars[i[1:]] = [buf, msg]
                        elif i == "@":
                            self.send(msg)
                        command = []
                        wait = "command"
                elif wait == "command":
                    command.append(i)
            if len(command) > 0:
                self.send(self.execute(command[0], command[1:])[1])


class Console:
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.config, self.logger = get_data()
        self.cexr = ConsoleExecutor(self.sock, self.addr, self.config, self.logger)

    def send(self, message):
        self.sock.sendto(dumps(message).encode("utf8"), self.addr)
        self.logger.debug(f"Сообщение отправлено клиенту '{self.addr[0]}:{self.addr[1]}':", message)

    def close(self):
        try:
            self.send(["something_wrong"])
            self.logger.info(f"Клиент '{self.addr[0]}:{self.addr[1]}' вызвал ошибку на сервере")
        except OSError:
            pass

    def receive(self, data):
        try:
            jdt = loads(data.decode("utf8"))

            com = jdt[0]
            args = jdt[1:]

            if com == "console_command":
                self.cexr.execute_text(" ".join(args))

        except BaseException as e:
            self.logger.error(e)
            self.close()
            if self.config["debug"]:
                raise
