class Item(object):

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if self.fields.has_key(name):
            self.fields[name] = value

    def set_fields(self):
        # Set all the keys as class attributes for easy access.
        for key in self.fields.iterkeys():
            if not hasattr(self, key):
                setattr(self, key, self.fields[key])
