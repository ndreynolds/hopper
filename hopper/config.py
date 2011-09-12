import os
import sys
from configobj import ConfigObj

from hopper.files import BaseFile, ConfigFile

class Config(ConfigFile):
    '''
    Reads and writes the .hprconfig file.

    The Config class holds defaults for the configuration and depends 
    on the parent class, ConfigFile, to do the actual reading and 
    writing.
    '''

    def __init__(self, path=None):
        # set config file fields
        self.fields = {
                'user': {
                    'name': None,
                    'email': None
                    },
                'core': {
                    'editor': 'vim',
                    'autocommit': True,
                    'color': True
                    }
                }
        # set field types (so they're parsed correctly)
        self.types = {
                'core': {
                    'autocommit': bool,
                    'color': bool
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

    def decorate(self, color, text, force=False):
        colors = {'purple' : '\033[95m',
                  'blue'   : '\033[94m',
                  'green'  : '\033[92m',
                  'yellow' : '\033[93m',
                  'red'    : '\033[91m',
                  'bold'   : '\033[1m'
                  }
        end = '\033[0m'
        # only output color if configed and output is not being
        # redirected (unless force is set).
        if self.core['color'] and (sys.stdout.isatty() or force):
            return colors[color] + text + end
        else:
            return text

def parse_gitconfig():
    '''Parse the .gitconfig file and return the dictionary.'''
    HOME = os.getenv('HOME')
    path = os.path.join(HOME, '.gitconfig')
    if not os.path.exists(path):
        return {}
    return ConfigObj(path).dict()
