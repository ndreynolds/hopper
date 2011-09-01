import os
import time

from git import Repo
from config import Config
from item import Item
from issue import Issue
from utils import to_json, from_json, match_path

class Tracker:
    '''
    Defines a Hopper tracker and provides paths to files within a 
    tracker.

    :param path: the relative or absolute path to the tracker
    '''
    def __init__(self, path):
        if not os.path.exists(path):
            path = match_path(path)
            if path is None:
                raise SystemExit('Supplied path does not exist')
        self.path = path
        self.fields = {
                'name': None,
                'created': None
                }
        self.paths = {
                'root': self.path,
                'issues': os.path.join(self.path, 'issues'),
                'hopper': os.path.join(self.path, '.hopper')
                }
        self.properties = {
                'name': None
                }
                
    @classmethod
    def new(cls, path):
        '''Create and return tracker at the given path.'''
        root = path
        # stores issues
        issues = os.path.join(root, 'issues')
        # stores administrative stuff 
        hopper = os.path.join(root, '.hopper')

        repo = Repo.init(root, mkdir=True)
        open(os.path.join(root, 'config'), 'w').close()
        os.mkdir(issues)
        open(os.path.join(issues, 'empty'), 'w').close()
        os.mkdir(hopper)
        open(os.path.join(hopper, 'empty'), 'w').close()
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

    def issue(self, sha):
        '''Return the Issue object with the given SHA1'''
        return Issue(self, sha)

    def issues(self, n=10, sort_by='updated', reverse=True, conditions=None):
        '''
        Return a list of n Issue objects filtered by conditions.

        :param n: the number of issues to return.
        :param sort_by: an attribute to sort the issues by (e.g. title)
        :param reverse: sort the issues in reverse order.
        :param conditions: a dictionary of keys that correspond to Issue
                           attributes and their required values. 
        Example:
        
        Retrieve the last 12 (or fewer) issues.
          >>> issues = tracker.issues(n=12)
          [<issue.Issue object>, ...]
          >>> len(issues) <= 12
          True
          >>> issues[0].title
          'Some Issue' 
        '''
        issues = [Issue(self, sha) for sha in self.get_issues()]
        if type(conditions) is dict:
            for key in conditions.keys():
                issues = filter(lambda x: getattr(x, key) == conditions[key],
                                issues)
        issues.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
        return issues

    def get_issue_path(self, sha, must_exist=True):
        '''
        Returns the absolute path to the issue if an issue with the
        given identifier exists, or if mustExist is False.  Returns
        None if the issue does not exist and mustExist is True (default).

        :param identifier: the SHA1 that uniquely identifies an issue.
        :param mustExist: whether or not the issue must exist to return a
                          path
        '''
        path = os.path.join(self.paths['issues'], sha)
        if os.path.exists(path) or not must_exist:
            return path
        return None

    def get_issues(self):
        '''
        Return a list of the SHA1s of all issues in the tracker.

        Use Tracker.issues() to get them as Issue objects, filtered by various
        conditions.
        '''
        # we'll just return any filenames in tracker/issues/ with 40 chars.
        return filter(lambda x: len(x) == 40, os.listdir(self.paths['issues']))
