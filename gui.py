from tkinter import *


class Window(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = 0
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
