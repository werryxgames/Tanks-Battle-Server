class GlobalMessage:
    def __init__(self, type_, text):
        self.type = type_
        self.text = text

    def get(self):
        return (self.type, self.text)
