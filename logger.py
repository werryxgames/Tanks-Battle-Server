from datetime import datetime
from re import sub
from traceback import format_exc
from colorama import init, Fore, Style
from absolute import to_absolute


class Logger:
    LEVEL_NONE = 5
    LEVEL_CRITICAL = 4
    LEVEL_ERROR = 3
    LEVEL_WARNING = 2
    LEVEL_INFO = 1
    LEVEL_DEBUG = 0

    def __init__(self, level, loglevel):
        init()
        self.level = level
        self.loglevel = loglevel

    @staticmethod
    def date():
        dt = datetime.today()

        res = [str(dt.year)]

        if len(str(dt.month)) < 2:
            res.append("0" + str(dt.month))
        else:
            res.append(str(dt.month))

        if len(str(dt.day)) < 2:
            res.append("0" + str(dt.day))
        else:
            res.append(str(dt.day))

        if len(str(dt.hour)) < 2:
            res.append("0" + str(dt.hour))
        else:
            res.append(str(dt.hour))

        if len(str(dt.minute)) < 2:
            res.append("0" + str(dt.minute))
        else:
            res.append(str(dt.minute))

        if len(str(dt.second)) < 2:
            res.append("0" + str(dt.second))
        else:
            res.append(str(dt.second))

        return res

    def message(self, msg, level=LEVEL_INFO):
        if self.level <= level:
            print(msg)

        if self.loglevel <= level:
            with open(to_absolute("server.log"), "a", encoding="utf8") as f:
                dt = self.date()
                f.write(
                    "{" + \
                    f"{dt[2]}.{dt[1]}.{dt[0]} {dt[3]}:{dt[4]}:{dt[5]}" + \
                    "} " + \
                    sub(r"\x1b.*?m", r"", msg) + \
                    "\n"
                )

    def log_error_data(self, func=None):
        if func is None:
            func = self.error

        func(format_exc()[:-1], prefix="")

    def critical(self, *message, prefix="[Критическая ошибка] "):
        msg = []
        for i in message:
            msg.append(str(i))

        self.message(Fore.RED + prefix + " ".join(msg) + Fore.RESET, 4)

    def error(self, *message, prefix="[Ошибка] "):
        msg = []
        for i in message:
            msg.append(str(i))

        self.message(Style.BRIGHT + Fore.RED + prefix + " ".join(msg) + Style.RESET_ALL, 3)

    def warning(self, *message, prefix="[Предупреждение] "):
        msg = []
        for i in message:
            msg.append(str(i))

        self.message(Fore.YELLOW + prefix + " ".join(msg) + Fore.RESET, 2)

    def info(self, *message, prefix="[Инфо] "):
        msg = []
        for i in message:
            msg.append(str(i))

        self.message(prefix + " ".join(msg), 1)

    def debug(self, *message, prefix="[Отладка] "):
        msg = []
        for i in message:
            msg.append(str(i))

        self.message(Style.BRIGHT + Fore.BLACK + prefix + " ".join(msg) + Style.RESET_ALL, 0)
