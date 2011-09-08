import os
from configobj import ConfigObj

from hopper.config_file import ConfigFile
from hopper.base_file import BaseFile

class Config(ConfigFile):
    '''
    Reads and writes the .hprconfig file.

    The Config class holds defaults for the configuration and depends 
    on the parent class, ConfigFile, to do the actual reading and 
    writing.
    '''

    def __init__(self, path=None):
        self.fields = {
                'user': {
                    'name': None,
                    'email': None
                    },
                'core': {
                    'editor': 'vim',
                    'autocommit': True
                    }
                }
        self.types = {
                'core': {
                    'autocommit': bool
                    }
                }
        if path is None:
            HOME = os.getenv('HOME')
            hprconfig = os.path.join(HOME, '.hprconfig')
            if os.path.exists(hprconfig):
                path = hprconfig
        self.path = path
        if self.path is not None and os.path.exists(self.path):
            self.from_file(path, self.types)
        super(BaseFile, self).__init__()

        # We really need a name and email, so we'll try
        # and steal them from $HOME/.gitconfig if they are
        # there but missing here.
        gitconfig = parse_gitconfig()
        if gitconfig:
            if self.user['name'] is None:
                try:
                    self.user['name'] = gitconfig['user']['name']
                except KeyError:
                    pass
            if self.user['email'] is None:
                try:
                    self.user['email'] = gitconfig['user']['email']
                except KeyError:
                    pass

    def save(self):
        self.to_file(self.path)

def parse_gitconfig():
    '''Parse the .gitconfig file and return the dictionary.'''
    HOME = os.getenv('HOME')
    path = os.path.join(HOME, '.gitconfig')
    if not os.path.exists(path):
        return {}
    return ConfigObj(path).dict()
