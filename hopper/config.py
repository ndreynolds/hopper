from configobj import ConfigObj

class Config(object):
    def __init__(self, path):
        self.path = path
        self.config = ConfigObj(path)
        self.defautls = {
                'name': None,
                'creator': None,
                }

    def write():
