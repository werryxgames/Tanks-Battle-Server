"""Updates file accounts.json, saving all the data."""
from json import dumps
from json import loads
from sys import argv

VERSION = 1
USAGE = "python update/accounts.py <path to accounts.json>"


def main(args):
    """Programm entry point."""
    if len(args) != 1:
        raise ValueError(f"Usage: {USAGE}")

    data = None

    with open(args[0], encoding="utf8") as file:
        data = loads(file.read())

    for acc_index, account in enumerate(data):
        new_account = {}

        if "guns" in account and "pts" in account:
            account["tanks"] = account["pts"]
            account["selected_tank"] = account["selected_pt"]
            account.pop("guns")
            account.pop("pts")
            account.pop("selected_gun")
            account.pop("selected_pt")

            if 0 not in account["tanks"]:
                account["tanks"] = [0] + account["tanks"]

            if account["selected_tank"] == -1:
                account["selected_tank"] = 0

        for key, value in account.items():
            if key in [
                "nick",
                "password",
                "xp",
                "crystals",
                "tanks",
                "selected_tank",
                "settings"
            ]:
                new_account[key] = value

        data[acc_index] = new_account

    result = dumps(data, indent=4, ensure_ascii=False)
    return result


if __name__ == '__main__':
    result_ = main(argv[1:])

    with open(argv[1], "w", encoding="utf8") as file_:
        file_.write(result_)
