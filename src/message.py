"""Module with messages."""


class GlobalMessage:
    """Class for global message."""

    def __init__(self, type_, text):
        """Initialization of global message."""
        self.type = type_
        self.text = text

    def get(self):
        """Returns message content."""
        return (self.type, self.text)
