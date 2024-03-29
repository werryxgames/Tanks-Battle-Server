"""Module for message logging."""
from datetime import datetime
from re import sub
from traceback import format_exc

from colorama import Fore
from colorama import Style
from colorama import init

from absolute import to_absolute


class Logger:
    """Class for message logging."""

    LEVEL_NONE = 6
    LEVEL_CRITICAL = 5
    LEVEL_ERROR = 4
    LEVEL_WARNING = 3
    LEVEL_INFO = 2
    LEVEL_DEBUG = 1
    LEVEL_SLOW = 0

    def __init__(self, level, loglevel):
        """Constructor for Logger."""
        init()
        self.level = level
        self.loglevel = loglevel

    @staticmethod
    def string2level(string, default=None):
        """Returns level of logger from string or default."""
        if default is None:
            default = Logger.LEVEL_INFO

        if string in ["n", "6", "none"]:
            return Logger.LEVEL_NONE

        if string in ["c", "5", "critical"]:
            return Logger.LEVEL_CRITICAL

        if string in ["e", "4", "error"]:
            return Logger.LEVEL_ERROR

        if string in ["w", "3", "warning"]:
            return Logger.LEVEL_WARNING

        if string in ["i", "2", "info"]:
            return Logger.LEVEL_INFO

        if string in ["d", "1", "debug"]:
            return Logger.LEVEL_DEBUG

        if string in ["s", "0", "slow"]:
            return Logger.LEVEL_SLOW

        return default

    @staticmethod
    def date():
        """Returns current date."""
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
        """Writes and prints message to screen and file."""
        if self.level <= level:
            print(msg)

        if self.loglevel <= level:
            with open(to_absolute("../server.log"), "a", encoding="utf8") as f:
                dt = self.date()
                f.write(
                    "{" + f"{dt[2]}.{dt[1]}.{dt[0]} {dt[3]}:{dt[4]}:\
{dt[5]}" + "} " + sub(r"\x1b.*?m", r"", msg) + "\n"
                )

    def log_error_data(self, func=None):
        """Calls func with last Traceback."""
        traceback = format_exc()[:-1]

        if "\nSystemExit: " not in traceback:
            if func is None:
                func = self.error

            func(traceback, prefix="")

    @staticmethod
    def join_message(message):
        """Joins message to string."""
        msg = []

        for i in message:
            msg.append(str(i))

        return " ".join(msg)

    def critical(self, *message, prefix="[Critical error] "):
        """Prints critical error."""
        self.message(
            Fore.RED + prefix + self.join_message(message) + Fore.RESET,
            self.LEVEL_CRITICAL
        )

    def error(self, *message, prefix="[Error] "):
        """Prints error."""
        self.message(
            Style.BRIGHT + Fore.RED + prefix + self.join_message(
                message
            ) + Style.RESET_ALL,
            self.LEVEL_ERROR
        )

    def warning(self, *message, prefix="[Warning] "):
        """Prints warning."""
        self.message(
            Fore.YELLOW + prefix + self.join_message(message) + Fore.RESET,
            self.LEVEL_WARNING
        )

    def info(self, *message, prefix="[Info] "):
        """Prints informational message."""
        self.message(
            prefix + self.join_message(message),
            self.LEVEL_INFO
        )

    def debug(self, *message, prefix="[Debug] "):
        """Prints debug message."""
        self.message(
            Style.BRIGHT + Fore.BLACK + prefix + self.join_message(
                message
            ) + Style.RESET_ALL,
            self.LEVEL_DEBUG
        )

    def slow(self, *message, prefix="[Debug (game)] "):
        """Prints very verbose information (slow)."""
        self.message(
            Style.BRIGHT + Fore.BLACK + prefix + self.join_message(
                message
            ) + Style.RESET_ALL,
            self.LEVEL_SLOW
        )
