import os
from os.path import join as pjoin
import time

from git import Repo
from utils import to_json, from_json, match_path
from config import Config
from item import Item

class Tracker:
    def __init__(self, path):
        '''
        Defines a Hopper tracker and provides paths to files within a 
        tracker.

        :param path: the relative or absolute path to the tracker
        '''
        if not os.path.exists(path):
            path = match_path(path)
            if path is None:
                raise SystemExit('Supplied path does not exist')
        self.path = path
        self.paths = {
                'root': self.path,
                'issues': os.path.join(self.path, 'issues'),
                'cache': os.path.join(self.path, 'cache')
                }
        self.config = Config()
        self.properties = {
                'name': None
                }
                
    @classmethod
    def create(cls, path):
        '''Create a tracker with the given properties.'''
        root = path
        issues = os.path.join(root, 'issues')
        cache = os.path.join(root, 'cache')

        repo = Repo.init(root, mkdir=True)
        os.mkdir(issues)
        open(os.path.join(issues, 'empty'), 'w').close()
        os.mkdir(cache)
        open(os.path.join(cache, 'empty'), 'w').close()
        repo.add_all()
        repo.commit(author='Hopper <hopper@hopperhq.com>',
                    message='Initial Commit')
        return cls(path)

    def read(self):
        '''Read in the tracker's properties.'''
        pass

    def update(self):
        '''Update the tracker's properties.'''
        pass

    def get_issue_path(self, identifier, must_exist=True):
        '''
        Returns the absolute path to the issue if an issue with the
        given identifier exists, or if mustExist is False.  Returns
        None if the issue does not exist and mustExist is True (default).

        :param identifier: the SHA1 that uniquely identifies an issue.
        :param mustExist: whether or not the issue must exist to return a
                          path
        '''
        path = pjoin(self.paths['issues'], identifier)
        if os.path.exists(path) or not must_exist:
            return path
        return None
