from configobj import ConfigObj

class Config(object):
    def __init__(self, path):
        self.path = path
        self.config = ConfigObj(path)
        self.defaults = {
                'name': None,
                'creator': None,
                }

    def write(self):
        pass
