"""GUI module."""
from tkinter import Tk


class Window(Tk):
    """Tkinter's window."""

    STATE_MAIN = 0
    STATE_CONSOLE = 1
    STATE_LOG = 2
    STATE_CONFIG = 3

    def __init__(self, *args, **kwargs):
        """Window initialization."""
        super().__init__(*args, **kwargs)
        self.state = self.STATE_MAIN
        self.elements = []

    def place(self, el, el_params, **place_params):
        """Places element."""
        elem = el(self, **el_params)
        elem.place(**place_params)

        self.elements.append(elem)

    def clear(self, state):
        """Clears all elements."""
        for i in self.elements:
            i.destroy()

        self.elements = []
        self.state = state
