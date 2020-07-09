class Link:
    def __init__(self, link):
        self.link = link
        self.weight = 0

    """ def __getattr__(self, key):
        if key == 'weight':
            return self.weight
        return self.link.__getattribute__(key)

    def __setattr__(self, key, value):
        if key == 'weight':
            self.weight = value
        else:
            self.link.__setattribute__(key, value) """