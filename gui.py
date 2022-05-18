from tkinter import *


class Window(Tk):
    STATE_MAIN = 0
    STATE_CONSOLE = 1
    STATE_LOG = 2
    STATE_CONFIG = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = self.STATE_MAIN
        self.elements = []

    def place(self, el, el_params, **place_params):
        elem = el(self, **el_params)
        elem.place(**place_params)

        self.elements.append(elem)

    def clear(self, state):
        for i in self.elements:
            i.destroy()

        self.elements = []
        self.state = state
