from __future__ import with_statement
import os
from configobj import ConfigObj

from hopper.base_file import BaseFile

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
        
        You can pass it a dictionary mapping fields to types and
        they will be auto-converted. That is, provide each field
        as a key and a type object (e.g. int, bool, str) as the
        value. You can nest dictionaries too.

        It should look like this:
            { 'autocommit': bool, 'user': {'name': str} }

        If str fields are mapped in types, empty strings remain ''.
        If they're not mapped, empty strings get converted to None.
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
