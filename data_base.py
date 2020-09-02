
class DataBase:
    def __init__(self, filename):
        self.filename = filename
        self.users = None
        self.file = None
        self.load()

    def load(self):
        self.file = open(self.filename, "r")
        if self.file.mode == 'r':
            read_data = self.file.read()
            return read_data.split(';')
        self.file.close()

