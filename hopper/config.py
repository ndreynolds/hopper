"""Classes for handling configuration settings."""

import os
import sys
from configobj import ConfigObj

from hopper.files import BaseFile, ConfigFile
from hopper.utils import get_uuid

class UserConfig(ConfigFile):
    """
    Reads and writes the .hprconfig file.

    The Config class holds (and intelligently sets) defaults for 
    the configuration. It depends on the parent class, ConfigFile, 
    to do the actual reading and writing.

    :param path: path to the config file, defaults to $HOME/.hprconfig.
                 If *that* doesn't exist, it will use the defaults. 
                 
    UserConfig objects will not write to the config file unless save() is 
    explicitly called.
    """
    def __init__(self, path=None):
        # set config file fields
        self.fields = {
                'user': {
                    'name' : None,
                    'email': None
                    },
                'core': {
                    'editor'    : 'vim',
                    'autocommit': True,
                    'color'     : True
                    },
                'web' : {
                    # This generated key is overridden if it exists
                    # in the config file already. It is required for the
                    # Flask app.
                    'secret_key': get_uuid() 
                    }
                }
        # set field types (so they're parsed correctly).
        # default type is string, so most don't need to be set.
        # see the ConfigFile class for more info.
        self.types = {
                'core': {
                    'autocommit': bool,
                    'color'     : bool
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
        """Write config to file."""
        self.to_file(self.path)

    def decorate(self, color, text, force=False):
        """
        Output coloring using ANSI escape codes.

        Returns colored :text using :color if the config setting
        for color is True. Otherwise, it just returns the text, unchanged.

        If STDOUT is being redirected, and :force is not True, it
        will not apply the coloring. This way the text can be written
        to file or piped without appearing garbled.

        :param color: a color from the colors dictionary below.
        :param text: str or unicode type value.
        :param force: force the colors, even if STDOUT != STDIN
        """
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


class TrackerConfig(ConfigFile):
    """
    Reads and writes the $TRACKER/config file.

    The tracker config file contains settings and preferences for
    the tracker.

    :param tracker: a Tracker object to glean the config path from.
    """
    def __init__(self, tracker):
        self.fields = {
                'name': None,
                'hq'  : {
                        # For Github post-receive hooks.
                        'github_repo_url' : None,
                        'github_repo_name': None
                        }
                }
        self.path = tracker.paths['config']
        if self.path is not None and os.path.exists(self.path):
            self.from_file(self.path)
        super(BaseFile, self).__init__()

    def save(self):
        """Save the tracker configuration to file."""
        self.to_file(self.path)


def parse_gitconfig():
    """Parse the .gitconfig file and return the dictionary."""
    HOME = os.getenv('HOME')
    path = os.path.join(HOME, '.gitconfig')
    if not os.path.exists(path):
        return {}
    return ConfigObj(path).dict()
