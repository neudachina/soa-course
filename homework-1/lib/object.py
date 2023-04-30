class Object:
    def __init__(self):
        self.integer = None
        self.floating = None
        self.str = None
        self.list = None
        self.dictionary = None

    def update(self, entries):
        self.integer = int(entries['integer'])
        self.floating = float(entries['floating'])
        self.str = entries['str']
        self.list = [int(value) for value in entries['list']]
        self.dictionary = entries['dictionary']

    def create_default(self):
        self.integer = 42
        self.floating = 3.1415
        self.str = "hello, world!"
        self.list = [1, 2, 3]
        self.dictionary = {'a': "a", 'b': "b", 'c': "c"}
