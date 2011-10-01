from __future__ import with_statement
import os
import time
from configobj import ConfigObj

from hopper.utils import from_json, to_json

class BaseFile(object):
    '''
    BaseFile subclasses have the 'fields' attribute, a dictionary that 
    specifies properties that will be saved to persistent memory.
    (Issues have 'content', 'timestamp', etc.)

    To make life easier, the class provides attribute access and
    assignment to these keys, provided they don't clash with any existing
    attributes.
    '''

    def __init__(self):
        self._set_fields()

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


class JSONFile(BaseFile):
    '''
    JSONFile subclasses the BaseFile class to provide methods
    for reading and writing JSON to file.
    '''

    def from_file(self, f):
        '''Read self.fields from file.'''
        if not os.path.exists(f):
            raise OSError('File does not exist')
        # uses a LockedFile object for file I/O
        with lock(f, 'r') as fp:
            self.fields = from_json(fp.read())
        return True

    def to_file(self, f):
        '''Save self.fields to file.'''
        if not type(self.fields) is dict:
            raise TypeError('self.fields must be a dict')
        with lock(f, 'w') as fp:
            fp.write(to_json(self.fields))
        return True


class ConfigFile(BaseFile):
    '''
    ConfigFile subclasses BaseFile to provide methods for
    writing to and reading from configuration files, using
    the ConfigObj module.

    ConfigFile subclasses still use the self.fields attribute
    to store their configuration. This class takes care of
    turning that into a configuration file.
    '''

    def from_file(self, f, types=None):
        '''
        Read self.fields from config file.
        
        :param f: path to file
        :param types: dictionary that maps fields to data types.
            By default, all fields will be assumed to be strings.
            Often, config files contain bools and ints. If you
            map the field to a type, it can be parsed for you.
            (i.e. if the string is ``'true'`` and type is bool,
            you get ``True``)

        The types dictionary should look something like this: 
            ``{ 'autocommit': bool, 'user': {'name': str} }``

        Provide the type objects themselves as values to the
        keys (which should be fields). The dictionary can be
        nested to your heart's content.

        If str fields are explicitly mapped to types, empty strings 
        remain ``''``. If the default behavior is being used, empty 
        strings get converted to None.
        '''
        def config_traverse(config, types):
            '''
            Recursively set types, config is mutable so no need for
            a return.
            '''
            # iterate through the types
            for k in types.keys():
                print k
                # if it has a matching key from the config:
                if k in config.keys():
                    if type(types[k]) is dict and type(config[k]) is dict:
                        # recurse deeper if both keys are dicts
                        config_traverse(config[k], types[k])
                    if types[k] is int:
                        try:
                            config[k] = int(config[k])
                        except TypeError:
                            config[k] = None
                        except ValueError:
                            config[k] = None
                    if types[k] is bool:
                        if config[k].lower() in ['1', 'on', 'true']:
                            config[k] = True
                        elif config[k].lower() in ['0', 'off', 'false']:
                            config[k] = False
                    # Reset empty strings from None if type is str.
                    if types[k] is str:
                        if config[k] is None:
                            config[k] = ''

        if not os.path.exists(f):
            raise OSError('File does not exist')
        config = ConfigObj(f).dict()
        # set empty strings to None
        for v in config.values():
            if v == '':
                v = None
        if type(types) is dict:
            config_traverse(config, types)
        # merge and set self.fields.
        self.fields = dict(self.fields.items() + config.items())

    def to_file(self, f):
        '''Save self.fields to file using ConfigObj.'''
        if not os.path.exists(f):
            raise OSError('File does not exist')
        config = ConfigObj(indent_type='    ')
        config.filename = f
        for k in self.fields.keys():
            config[k] = self.fields[k]
        config.write()


class LockedFile(file):
    '''
    Provides primitive file-locking. It subclasses the ``file`` object
    to hook in locking and unlocking. Hopper is single-threaded, but there
    may be multiple processes acting on a Tracker's files at any time. As
    such, we need a little insurance.

    Locks are set by creating a file of the same path, but suffixed with
    ``.lock``. Both reading and writing requires an exclusive lock. 

    Before opening the file, we lock it. After closing it, we unlock it.

    :param persist: if True, keep trying until the file is unlocked or a
                    timeout is reached. 
    :param interval: interval in ms at which to poll ``self.locked()``.
    :param surrender: time in ms, after which the method will give up and
                      throw an exception. Note that this can only be 
                      applied approximately.
    '''
    # TODO multiple readers, exclusive writer

    def __init__(self, name, mode, persist=True, 
                 surrender=2000, interval=10):

        # we don't care if the file exists (it may be new)
        # let the file object worry about that.
        self.path = name
        self.lock_path = name + '.lock'
        self.persist = persist
        self.surrender = surrender
        self.interval = interval

        # see if it's locked
        if self.locked():
            # if it is, we'll wait around
            self.wait()
        self.lock()
        file.__init__(self, name, mode)

    def __del__(self):
        '''
        Last ditch effort to unlock files.

        LockFiles should be closed (and by extension, unlocked) by
        calling the ``close`` method or using the ``with`` statement. 
        The ``__del__`` method is in place to remove the lock if these
        are forgotten, but it's not guaranteed to work (due to the way
        python calls ``__del__``.
        '''
        self.unlock()

    def __exit__(self, type, value, traceback):
        '''Unlock the file when object falls out of ``with`` scope.'''
        file.__exit__(self, type, value, traceback)
        self.unlock()

    def close(self):
        file.close(self)
        self.unlock()

    def locked(self):
        '''Check if the file is locked.'''
        if os.path.isfile(self.lock_path):
            return True
        return False

    def lock(self):
        '''Lock the file.'''
        open(self.lock_path, 'w').close()

    def unlock(self):
        '''Unlock a file.'''
        if self.locked():
            os.remove(self.lock_path)

    def wait(self):
        '''
        Continually poll the ``locked`` method using the given interval
        until either the file can be acquired or the timeout is reached.

        :raise RuntimeError: if duration exceeds surrender value.
        '''
        t = 0
        while self.locked():
            if t > self.surrender:
                raise RuntimeError('Acquiring lock timed out')
            time.sleep(float(self.interval) / 1000)
            t += self.interval


def lock(name, mode):
    '''
    Returns a LockedFile object with the default timeout.

    :param name: path to the file
    :param mode: mode to open the file with
    '''
    return LockedFile(name, mode)
