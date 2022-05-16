from sys import argv
from mjson import read
from network import start_server, start_server_async
from logger import Logger
from singleton import set_data
from tests import tests
from absolute import to_absolute
from tkinter import PhotoImage
from tkinter.ttk import Label, Button, Style
from gui import Window


def init_window(config, logger):
    win = Window()
    win.wm_title("Tanks Battle Server")
    win.geometry("600x320")
    win.tk.call("wm", "iconphoto", win._w, PhotoImage(file=to_absolute("icon.png", temp=True)))
    win.configure(background="#555")

    style = Style(win)
    style.theme_use("clam")
    style.configure("TLabel", background="#555", foreground="#ddd")
    style.configure("TButton", background="#333", foreground="#ddd", relief="flat", borderwidth=0)
    style.map("TButton", background=[("pressed", "#222"), ("active", "#2c2c2c")], foreground=[("pressed", "#eee"), ("active", "#dadada")])

    win.place(Label, {"text": "Tanks Battle Server", "font": "Arial 30 bold"}, relx=0.5, rely=0, y=10, anchor="n")
    win.place(Label, {"text": "Сервер", "font": "Arial 20"}, relx=0.5, rely=0, y=75, anchor="n")
    win.place(Label, {"text": "Статус: не запущен", "font": "Arial 16"}, relx=0, rely=0, x=10, y=140, anchor="nw")
    win.place(Button, {"text": "Запустить", "command": start_server_async}, relx=1, rely=0, x=-10, y=140, anchor="ne")
    win.place(Label, {"text": f"Порт: {config['port']}", "font": "Arial 16"}, relx=0, rely=0, x=10, y=180, anchor="nw")
    win.place(Button, {"text": "Настроить"}, relx=1, rely=0, x=-10, y=180, anchor="ne")
    win.place(Label, {"text": "Консоль", "font": "Arial 16"}, relx=0, rely=0, x=10, y=220, anchor="nw")
    win.place(Button, {"text": "Перейти"}, relx=1, rely=0, x=-10, y=220, anchor="ne")
    win.place(Label, {"text": "Лог", "font": "Arial 16"}, relx=0, rely=0, x=10, y=260, anchor="nw")
    win.place(Button, {"text": "Показать"}, relx=1, rely=0, x=-10, y=260, anchor="ne")
    win.place(Label, {"text": "Github: https://github.com/werryxgames/Tanks-Battle-Server", "font": "Arial 8"}, relx=0, rely=1, x=2, y=-2, anchor="sw")
    win.place(Label, {"text": "Вебсайт: https://werryxgames.ml", "font": "Arial 8"}, relx=1, rely=1, x=-2, y=-2, anchor="se")

    set_data(config, logger, win)

    win.mainloop()


def main():
    logger = Logger(Logger.LEVEL_INFO, Logger.LEVEL_INFO)
    config = read("config.json")

    check_tests = True

    for i in argv:
        if i.lower() == "--notests":
            check_tests = False
            break

    if not check_tests or tests.main(True):
        try:
            show_gui = True

            for i in argv:
                if i.lower() == "--nogui":
                    show_gui = False
                    break

            if show_gui:
                logger = Logger(Logger.LEVEL_CRITICAL, Logger.LEVEL_INFO)
                init_window(config, logger)
            else:
                set_data(config, logger)
                start_server(config, logger)

        except:
            logger.log_error_data(logger.critical)
    else:
        logger.critical("Один из тестов провален")


if __name__ == '__main__':
    main()
