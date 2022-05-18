from sys import argv
from json.decoder import JSONDecodeError
from mjson import read
from network import start_server, start_server_async, stop_server, is_active
from logger import Logger
from singleton import set_data
from tests import tests
from absolute import to_absolute
from tkinter import PhotoImage, Text, Entry, Tk
from tkinter.messagebox import showerror
from tkinter.ttk import Label, Button, Style
from gui import Window
from console import ConsoleExecutor
from close import stop


def current_clear(win):
    if win.state == Window.STATE_CONSOLE:
        el = win.elements[2]
    elif win.state == Window.STATE_LOG:
        el = win.elements[1]
        with open(to_absolute("server.log"), "wb"):
            pass
    else:
        return

    el.configure(state="normal")
    el.delete("1.0", "end")
    el.configure(state="disabled")


def console_run(win, ce):
    if win.state == Window.STATE_CONSOLE:
        text = win.elements[1].get()
        win.elements[1].delete(0, "end")
        win.elements[2].configure(state="normal")
        win.elements[2].insert("end", f"> {text}\n")
        win.elements[2].configure(state="disabled")

        ce.execute_text(text)


def save_config(win):
    if win.state == Window.STATE_CONFIG:
        text = win.elements[1].get("1.0", "end")[:-1]
        with open(to_absolute("config.json"), "w", encoding="utf8") as f:
            f.write(text)


def tab_config(config, win):
    win.clear(Window.STATE_CONFIG)

    win.place(Label, {"text": "Конфигурация", "font": "Arial 30 bold"}, relx=0.5, rely=0, y=10, anchor="n")
    win.place(Text, {"font": "Arial 12", "background": "#555", "foreground": "#ddd", "relief": "flat", "highlightthickness": 0, "insertbackground": "#ddd", "insertwidth": 1}, relx=0, rely=0, x=5, y=62, relw=1, w=-10, relh=1, h=-100, anchor="nw")
    win.place(Button, {"text": "Вернуться", "command": lambda: tab_main(config, win)}, relx=0, rely=1, x=5, y=-5, anchor="sw")
    win.place(Button, {"text": "Сохранить", "command": lambda: save_config(win)}, relx=1, rely=1, x=-5, y=-5, anchor="se")

    with open(to_absolute("config.json"), encoding="utf8") as f:
        win.elements[1].insert("end", f.read())


def tab_console(config, win):
    win.clear(Window.STATE_CONSOLE)

    ce = ConsoleExecutor(win=win)

    win.place(Label, {"text": "Консоль", "font": "Arial 30 bold"}, relx=0.5, rely=0, y=10, anchor="n")
    win.place(Entry, {"font": "Arial 12", "background": "#555", "foreground": "#ddd", "relief": "flat", "highlightthickness": 0, "insertbackground": "#ddd", "insertwidth": 1}, relx=0, rely=0, x=5, y=62, relw=1, w=-10, h=20, anchor="nw")
    win.place(Text, {"font": "Arial 12", "state": "disabled", "background": "#555", "foreground": "#ddd", "relief": "flat", "highlightthickness": 0}, relx=0, rely=0, x=5, y=87, relw=1, w=-10, relh=1, h=-125, anchor="nw")
    win.place(Button, {"text": "Вернуться", "command": lambda: tab_main(config, win)}, relx=0, rely=1, x=5, y=-5, anchor="sw")
    win.place(Button, {"text": "Очистить", "command": lambda: current_clear(win)}, relx=0.5, rely=1, y=-5, anchor="s")
    win.place(Button, {"text": "Отправить", "command": lambda: console_run(win, ce)}, relx=1, rely=1, x=-5, y=-5, anchor="se")

    win.elements[1].bind("<Return>", lambda e: win.elements[5].invoke())


def tab_log(config, win):
    win.clear(Window.STATE_LOG)

    win.place(Label, {"text": "Лог", "font": "Arial 30 bold"}, relx=0.5, rely=0, y=10, anchor="n")
    win.place(Text, {"font": "Arial 12", "background": "#555", "foreground": "#ddd", "relief": "flat", "highlightthickness": 0}, relx=0, rely=0, x=5, y=62, relw=1, w=-10, relh=1, h=-100, anchor="nw")
    win.place(Button, {"text": "Вернуться", "command": lambda: tab_main(config, win)}, relx=0, rely=1, x=5, y=-5, anchor="sw")
    win.place(Button, {"text": "Очистить", "command": lambda: current_clear(win)}, relx=1, rely=1, x=-5, y=-5, anchor="se")

    with open(to_absolute("server.log"), encoding="utf8") as f:
        win.elements[1].insert("end", f.read())
        win.elements[1].configure(state="disabled")


def tab_main(config, win):
    win.clear(Window.STATE_MAIN)

    win.place(Label, {"text": "Tanks Battle Server", "font": "Arial 30 bold"}, relx=0.5, rely=0, y=10, anchor="n")
    win.place(Label, {"text": "Сервер", "font": "Arial 20"}, relx=0.5, rely=0, y=75, anchor="n")
    win.place(Label, {"text": "Статус: не запущен", "font": "Arial 16"}, relx=0, rely=0, x=10, y=140, anchor="nw")
    win.place(Button, {"text": "Запустить", "command": start_server_async}, relx=1, rely=0, x=-10, y=140, anchor="ne")
    win.place(Label, {"text": f"Порт: {config['port']}", "font": "Arial 16"}, relx=0, rely=0, x=10, y=180, anchor="nw")
    win.place(Button, {"text": "Настроить", "command": lambda: tab_config(config, win)}, relx=1, rely=0, x=-10, y=180, anchor="ne")
    win.place(Label, {"text": "Консоль", "font": "Arial 16"}, relx=0, rely=0, x=10, y=220, anchor="nw")
    win.place(Button, {"text": "Перейти", "command": lambda: tab_console(config, win)}, relx=1, rely=0, x=-10, y=220, anchor="ne")
    win.place(Label, {"text": "Лог", "font": "Arial 16"}, relx=0, rely=0, x=10, y=260, anchor="nw")
    win.place(Button, {"text": "Показать", "command": lambda: tab_log(config, win)}, relx=1, rely=0, x=-10, y=260, anchor="ne")
    win.place(Label, {"text": "Github: https://github.com/werryxgames/Tanks-Battle-Server", "font": "Arial 8"}, relx=0, rely=1, x=2, y=-2, anchor="sw")
    win.place(Label, {"text": "Вебсайт: https://werryxgames.ml", "font": "Arial 8"}, relx=1, rely=1, x=-2, y=-2, anchor="se")

    if is_active():
        win.elements[2].configure(text=f"Статус: запущен\tIP: {config['host']}")
        win.elements[3].configure(text="Остановить", command=stop_server)

def init_window(config, logger):
    win = Window()
    win.wm_title("Tanks Battle Server")
    win.geometry("600x320")
    win.tk.call("wm", "iconphoto", win._w, PhotoImage(file=to_absolute("icon.png", temp=True)))
    win.configure(background="#444")
    win.protocol("WM_DELETE_WINDOW", lambda: stop(0))

    style = Style(win)
    style.theme_use("clam")
    style.configure("TLabel", background="#444", foreground="#ddd")
    style.configure("TButton", background="#333", foreground="#ddd", relief="flat", borderwidth=0)
    style.map("TButton", background=[("pressed", "#222"), ("active", "#2c2c2c")], foreground=[("pressed", "#eee"), ("active", "#dadada")])

    tab_main(config, win)

    set_data(config, logger, win)

    win.mainloop()


def main():
    logger = Logger(Logger.LEVEL_INFO, Logger.LEVEL_INFO)
    try:
        config = read("config.json")
    except JSONDecodeError:
        logger.critical("Не удалось загрузить конфигурацию. Возможно файл был повреждён")

        gui = True

        for i in argv:
            if i.lower() == "--nogui":
                gui = False

        if gui:
            root = Tk()
            root.withdraw()
            showerror("Ошибка запуска Tanks Battle Server", "Не удалось загрузить конфигурацию. Возможно файл был повреждён")

        stop(1)


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
