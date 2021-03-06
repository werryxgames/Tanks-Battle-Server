from datetime import datetime
from re import sub
from traceback import format_exc
from colorama import init, Fore, Style
from absolute import to_absolute


class Logger:
    LEVEL_NONE = 6
    LEVEL_CRITICAL = 5
    LEVEL_ERROR = 4
    LEVEL_WARNING = 3
    LEVEL_INFO = 2
    LEVEL_DEBUG = 1
    LEVEL_SLOW = 0

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
        traceback = format_exc()[:-1]

        if "\nSystemExit: " not in traceback:
            if func is None:
                func = self.error

            func(traceback, prefix="")

    @staticmethod
    def join_message(message):
        msg = []

        for i in message:
            msg.append(str(i))

        return " ".join(msg)

    def critical(self, *message, prefix="[?????????????????????? ????????????] "):
        self.message(Fore.RED + prefix + self.join_message(message) + Fore.RESET, self.LEVEL_CRITICAL)

    def error(self, *message, prefix="[????????????] "):
        self.message(Style.BRIGHT + Fore.RED + prefix + self.join_message(message) + Style.RESET_ALL, self.LEVEL_ERROR)

    def warning(self, *message, prefix="[????????????????????????????] "):
        self.message(Fore.YELLOW + prefix + self.join_message(message) + Fore.RESET, self.LEVEL_WARNING)

    def info(self, *message, prefix="[????????] "):
        self.message(prefix + self.join_message(message), self.LEVEL_INFO)

    def debug(self, *message, prefix="[??????????????] "):
        self.message(Style.BRIGHT + Fore.BLACK + prefix + self.join_message(message) + Style.RESET_ALL, self.LEVEL_DEBUG)

    def slow(self, *message, prefix="[?????????????? (????????)] "):
        self.message(Style.BRIGHT + Fore.BLACK + prefix + self.join_message(message) + Style.RESET_ALL, self.LEVEL_SLOW)
