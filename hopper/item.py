from utils import to_json

class Item(object):
    '''
    Item subclasses have the 'fields' attribute, a dictionary that 
    specifies properties that will be saved to persistent memory.
    (Issues have 'content', 'timestamp', etc.)

    To make life easier, the Item class provides attribute access and
    assignment to these keys, provided they don't clash with any existing
    attributes.
    '''

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        # Update fields[name] if the key exists
        if self.fields.has_key(name):
            self.fields[name] = value

    def __getattribute__(self, name):
        '''
        We want the attributes to contain the same value as
        the fields[name] value. Assuming the fields dictionary was
        modified directly, the corresponding attribute would not be 
        in sync. To counter this, we get attributes directly from the
        dictionary.
        '''
        # we don't want to mess with any special attributes.
        if not name.startswith('__'):
            # use the base class's method so we avoid infinite recursion.
            fields = object.__getattribute__(self, 'fields')
            if fields.has_key(name):
                return self.fields[name]
        return object.__getattribute__(self, name)

    def _set_fields(self):
        '''
        Sets the keys in self.fields as attributes, provided they don't
        already exist. This needs to be called manually inside __init__.
        '''
        for key in self.fields.iterkeys():
            if not hasattr(self, key):
                setattr(self, key, self.fields[key])
