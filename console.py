from json import loads, dumps
from datetime import datetime
from singleton import get_data, get_matches
from message import GlobalMessage
from accounts import AccountManager


class ConsoleExecutor:
    def __init__(self, sock, addr, config, logger):
        self.sock = sock
        self.addr = addr
        self.config = config
        self.logger = logger

    def send(self, message):
        self.sock.sendto(dumps(["console_result", message]).encode("utf8"), self.addr)
        self.logger.debug(f"Результат команды отправлен клиенту '{self.addr[0]}:{self.addr[1]}':", message)

    def send_part(self, message):
        self.sock.sendto(dumps(["console_result_part", message]).encode("utf8"), self.addr)
        self.logger.debug(f"Часть результата команды отправлена клиенту '{self.addr[0]}:{self.addr[1]}':", message)

    def execute(self, com, args):
        if com == "account":
            if len(args) < 2:
                self.send("Ошибка команды")
                return

            nick = args[0]
            act = args[1]

            if act == "set":
                key = args[2]
                val = loads(args[3])
                status = AccountManager.set_account(nick, key, val)
                if status == AccountManager.SUCCESSFUL:
                    self.send(f"Установлено значение '{key}' в {val} для аккаунта '{nick}'")
                elif status == AccountManager.FAILED_NOT_FOUND:
                    self.send(f"Аккаунт не найден")
                elif status == AccountManager.FAILED_UNKNOWN:
                    self.send(f"Не удалось выполнить команду")
            elif act == "get":
                if len(args) > 2:
                    key = args[2]
                else:
                    key = None
                status = AccountManager.get_account(nick)
                if status == AccountManager.FAILED_NOT_FOUND:
                    self.send(f"Аккаунт не найден")
                elif status == AccountManager.FAILED_UNKNOWN:
                    self.send(f"Не удалось выполнить команду")
                else:
                    if key is None:
                        self.send(status)
                    else:
                        self.send(status[key])
            elif act == "del":
                key = args[2]
                status = AccountManager.del_account_key(nick, key)
                if status == AccountManager.SUCCESSFUL:
                    self.send(f"Удален ключ '{key}' для аккаунта '{nick}'")
                elif status == AccountManager.FAILED_NOT_FOUND:
                    self.send(f"Аккаунт не найден")
                elif status == AccountManager.FAILED_UNKNOWN:
                    self.send(f"Не удалось выполнить команду")
                elif status == AccountManager.FAILED_NOT_EXISTS:
                    self.send(f"Ключ '{key}' не найден в аккаунте '{nick}'")
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
                        self.send(s)
                    elif status == AccountManager.FAILED_NOT_FOUND:
                        self.send(f"Аккаунт не найден")
                    elif status == AccountManager.FAILED_UNKNOWN:
                        self.send(f"Не удалось выполнить команду")
                except (ValueError, IndexError):
                    self.send("Неверный синтаксис команды: 'account <никнейм> ban (<день>.<месяц>.<год> | -1) [причина]'")
            elif act == "unban":
                status = AccountManager.del_account_key(nick, "ban")
                if status == AccountManager.SUCCESSFUL:
                    self.send(f"Аккаунт '{nick}' разблокирован")
                elif status == AccountManager.FAILED_NOT_EXISTS:
                    self.send(f"Аккаунт '{nick}' ещё не заблокирован")
                elif status == AccountManager.FAILED_NOT_FOUND:
                    self.send(f"Аккаунт не найден")
                elif status == AccountManager.FAILED_UNKNOWN:
                    self.send(f"Не удалось выполнить команду")
            elif act == "remove":
                if len(args) == 2:
                    status = AccountManager.del_account(nick)
                    if status == AccountManager.SUCCESSFUL:
                        self.send(f"Аккаунт '{nick}' удалён")
                    elif status == AccountManager.FAILED_NOT_FOUND:
                        self.send(f"Аккаунт не найден")
                    elif status == AccountManager.FAILED_UNKNOWN:
                        self.send(f"Не удалось выполнить команду")
                else:
                    self.send("Команда 'account <никнейм> remove' не принимает аргументов. Возможно вы имели ввиду 'account <никнейм> del'")
            else:
                self.send("Команда не найдена")
        elif com == "player":
            if len(args) < 2:
                self.send("Ошибка команды")
                return

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
                self.send("Игрок не найден, или не в матче сейчас")
                return

            if act == "kick":
                battle["messages"].append(GlobalMessage("player_leave", nick))
                self.send("Игрок отключён от матча")
                return
            elif act == "battle":
                if len(args) < 3:
                    self.send("Ошибка команды")
                    return

                act2 = args[2]
                if act2 == "players":
                    pls = []
                    for pl in battle["players"]:
                        pls.append(pl.nick)
                    self.send(pls)
                elif act2 == "end":
                    del battles[battles.index(battle)]
                    self.send("Матч завершён")
                else:
                    self.send("Команда не найдена")
            else:
                self.send("Команда не найдена")
        else:
            self.send("Команда не найдена")

    def execute_text(self, text):
        spl = text.split()
        if len(spl) > 0:
            com = spl[0]
            args = spl[1:]

            self.execute(com, args)
        else:
            pass


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
