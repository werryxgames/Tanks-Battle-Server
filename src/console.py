"""Console module."""
from datetime import datetime
from json import dumps
from shlex import split as spl

from accounts import AccountManager
from message import GlobalMessage
from singleton import get_data
from singleton import get_matches


class ConsoleExecutor:
    """Runs console commands."""

    def __init__(
        self,
        sock=None,
        addr=None,
        config=None,
        logger=None,
        win=None,
        rudp=None
    ):
        """Initialization of console commands runner."""
        self.sock = sock
        self.addr = addr
        self.rudp = rudp
        self.config = config
        self.logger = logger
        self.win = win
        self.vars = {}

    def send(self, message):
        """Sends Reliable UDP message to client."""
        if self.sock is not None:
            self.rudp.send(["console_result", message])

        if self.logger is not None:
            if self.addr is not None:
                self.logger.debug(f"Results of command sent to player '\
{self.addr[0]}:{self.addr[1]}':", message)
        elif self.sock is None and self.win is not None and \
                self.win.state == self.win.STATE_CONSOLE:
            self.win.elements[2].configure(state="normal")
            self.win.elements[2].insert("end", str(message) + "\n")
            self.win.elements[2].configure(state="disabled")

    @staticmethod
    def get_value(value):
        """Returns value from string."""
        if value[0] == "\\":
            return value[1:]

        try:
            return int(value)
        except ValueError:
            return value

    @staticmethod
    def execute_ban_player(args):
        """Runs command to block player."""
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
                string = f"Account '{nick}' is blocked "

                if tstamp == -1:
                    string += "forever"
                else:
                    string += "until " + args[2]

                string += ", reason"

                if reason is None:
                    string += " not specified"
                else:
                    string += ": '" + reason + "'"

                return string

            if status == AccountManager.FAILED_NOT_FOUND:
                return "Account not found"

            return "Failed to run command"
        except (ValueError, IndexError):
            return "Invalid command syntax: 'account <никнейм> \
ban (<day>.<month>.<year> | -1) [reason]'"

    @staticmethod
    def execute_account_setget(args):
        """Sets/gets value of account."""
        nick = args[0]
        act = args[1]

        if act == "set":
            if len(args) <= 3:
                return "Invalid usage"

            key = args[2]
            val = ConsoleExecutor.get_value(args[3])

            status = AccountManager.set_account(nick, key, val)

            if status == AccountManager.SUCCESSFUL:
                string = f"Set value for '{key}' to "
                string += str(val) if isinstance(val, int) else f"'{val}'"
                string += f" for account '{nick}'"
                return string

            if status == AccountManager.FAILED_NOT_FOUND:
                return "Account not found"

            return "Failed to run command"

        if act == "get":
            status = AccountManager.get_account(nick)

            if status == AccountManager.FAILED_NOT_FOUND:
                return "Account not found"

            if status == AccountManager.FAILED_UNKNOWN:
                return "Failed to run command"

            return status[args[2]] if len(args) > 2 else status

        return None

    @staticmethod
    def execute_account_del(args):
        """Deletes account key."""
        if len(args) <= 2:
            return "Invalid usage"

        nick = args[0]
        key = args[2]
        status = AccountManager.del_account_key(nick, key)

        if status == AccountManager.SUCCESSFUL:
            return f"Key '{key}' deleted for account '{nick}'"

        if status == AccountManager.FAILED_NOT_FOUND:
            return "Account not found"

        if status == AccountManager.FAILED_UNKNOWN:
            return "Failed to run command"

        if status == AccountManager.FAILED_NOT_EXISTS:
            return f"Key '{key}' not found in account '{nick}'"

        return "Failed to run command"

    @staticmethod
    def execute_unban_player(args):
        """Unblocks player's account."""
        nick = args[0]
        status = AccountManager.del_account_key(nick, "ban")

        if status == AccountManager.SUCCESSFUL:
            return f"Account '{nick}' unblocked"

        if status == AccountManager.FAILED_NOT_EXISTS:
            return f"Аккаунт '{nick}' isn't blocked"

        if status == AccountManager.FAILED_NOT_FOUND:
            return "Account not found"

        return "Failed to run command"

    @staticmethod
    def execute_remove_account(args):
        """Deletes account."""
        if len(args) != 2:
            return "Command 'account <никнейм> remove' doesn't accept \
any arguments. Maybe you mean 'account <никнейм> del'?"

        nick = args[0]
        status = AccountManager.del_account(nick)

        if status == AccountManager.SUCCESSFUL:
            return f"Account '{nick}' deleted"

        if status == AccountManager.FAILED_NOT_FOUND:
            return "Account not found"

        return "Failed to run command"

    @staticmethod
    def execute_account(args):
        """Runs account command."""
        if len(args) < 2:
            return "Invalid usage"

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

        return "Unknown sub-command"

    @staticmethod
    def execute_player_battle(args, battle, battles):
        """Runs commmand for battle."""
        if len(args) < 3:
            return "Invalid syntax"

        act2 = args[2]

        if act2 == "players":
            pls = []

            for pl in battle["players"]:
                pls.append(pl.nick)

            return pls

        if act2 == "end":
            del battles[battles.index(battle)]
            return "Battle ended"

        return "Unknown sub-command"

    @staticmethod
    def execute_player(args):
        """Runs player command."""
        if len(args) < 2:
            return "Invalid usage"

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
            return "Player not found or not in battle now"

        if act == "kick":
            battle["messages"].append(GlobalMessage("player_leave", nick))
            return "Player disconnected"

        if act == "battle":
            return ConsoleExecutor.execute_player_battle(args, battle, battles)

        return "Unknown sub-command"

    @staticmethod
    def execute(com, args):
        """Runs command com with arguments args."""
        if com == "account":
            return ConsoleExecutor.execute_account(args)

        if com == "player":
            return ConsoleExecutor.execute_player(args)

        return "Command not found"

    def execute_text(self, text, main=True):
        """Runs command as text."""
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
    """Claas for commands console."""

    def __init__(self, sock, addr, rudp):
        """Initialization of console."""
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
        """Sends message to client."""
        self.sock.sendto(dumps(message).encode("utf8"), self.addr)
        self.logger.debug(
            f"Message sent to client '{self.addr[0]}:{self.addr[1]}':",
            message
        )

    def close(self):
        """Closes connection with client."""
        try:
            self.send(["something_wrong"])
            self.logger.info(f"Client '{self.addr[0]}:{self.addr[1]}' called \
server error")
        except OSError:
            pass

    def receive(self, jdt):
        """Handles data, received from client."""
        try:
            com = jdt[0]
            args = jdt[1:]

            if com == "console_command":
                self.cexr.execute_text(" ".join(args))

        except BaseException:
            self.logger.log_error_data()
            self.close()
            return
