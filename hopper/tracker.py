from __future__ import with_statement
import os

from hopper.git import Repo
from hopper.issue import Issue
from hopper.utils import match_path
from hopper.files import BaseFile, JSONFile

class Tracker(JSONFile):
    '''
    Defines a Hopper tracker and provides paths to files within a 
    tracker. It subclasses JSONFile to get methods for reading from
    and writing to its JSON config file.

    :param path: the relative or absolute path to the tracker
    '''
    def __init__(self, path):
        self.fields = {
                'name': None,
                'created': None
                }
        if not os.path.exists(path):
            path = match_path(path)
            if path is None:
                raise OSError('Supplied path does not exist')
        self.path = path
        self.paths = {
                'root': self.path,
                'config': os.path.join(self.path, 'config'),
                'issues': os.path.join(self.path, 'issues'),
                'hopper': os.path.join(self.path, '.hopper')
                }
        self.properties = {
                'name': None
                }
        self.repo = Repo(path)
        super(BaseFile, self).__init__()

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
        open(os.path.join(root, 'README.md'), 'w').close()

        readme_notes = '''\
**This is your Project Overview.**

It might contain notes on submitting issues, information about your
project, or both.

To replace this default message, edit the file `README.md` under 
`$TRACKER/README.md`.'''

        with open(os.path.join(root, 'README.md'), 'w') as fp:
            fp.write(readme_notes)
        os.mkdir(issues)
        open(os.path.join(issues, 'empty'), 'w').close()
        os.mkdir(hopper)
        open(os.path.join(hopper, 'empty'), 'w').close()
        repo.add_all()
        repo.commit(author='Hopper <hopper@hopperhq.com>',
                    message='Initial Commit')
        return cls(path)

    def autocommit(self):
        '''Commit any changes to the repo.'''
        self.repo.cmd(['add', '.'])
        self.repo.cmd(['commit', '-am', 'Did something'])

    def read(self, relpath, mode='r'):
        '''Read a file relative to the tracker route.'''
        path = os.path.join(self.paths['root'], relpath)
        with open(path, mode) as fp:
            return fp.read()

    def update(self):
        '''Update the tracker's properties.'''
        pass

    def issue(self, sha):
        '''Return the Issue object with the given SHA1'''
        return Issue(self, sha)

    def issues(self, n=None, offset=0, sort_by='updated', reverse=True, 
               return_num=False, conditions=None):
        '''
        Return a list of n Issue objects filtered by conditions.

        :param n: the number of issues to return. (returns all by default)
        :param offset: apply an offset to the return. If n=20 and offset=40,
                       issues 40-59 would be returned, assuming they exist.
                       (The first issue is 0, that's why we're not getting 41-60.)
                       This parameter was added with paging in mind.
        :param sort_by: an attribute to sort the issues by (e.g. title). By
                        default it will sort by 'updated', which will contain
                        the last-modified (or created) timestamp.
        :param reverse: return the sorted issues in reverse order.
        :param return_num: instead of only the list, return a tuple containing 
                           the list of issues and the total number of issues 
                           after filtering.
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

        The conditions parameter allows for very basic (x == y) filtering. 
        The Filter class has some more advanced methods. They can be used 
        on the return list. 
        '''
        issues = [Issue(self, sha) for sha in self.get_issues()]
        # filter first, sort second.
        if type(conditions) is dict:
            for key in conditions.keys():
                issues = filter(lambda x: getattr(x, key) == conditions[key],
                                issues)
        issues.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
        num_issues = len(issues)

        if type(n) is int:
            issues = issues[offset:(offset + n)]
        else:
            issues = issues[offset:]

        if return_num:
            return issues, num_issues
        else:
            return issues

    def history(self, n=10):
        '''
        Return a list of dictionaries containing the action and the actor.
        These are assembled from the Git repository's commit log.
        '''
        return self.repo.commits()

    def get_issue_path(self, sha):
        '''
        Returns the absolute path to the issue. It doesn't check if the issue
        exists; this should be done afterwards if necessary.

        :param sha: the SHA1 that uniquely identifies an issue.
        '''
        return os.path.join(self.paths['issues'], sha, 'issue')

    def get_issues(self):
        '''
        Return a list of the SHA1s of all issues in the tracker.

        Use Tracker.issues() to get them as Issue objects, filtered by various
        conditions.
        '''
        # we'll just return any paths in tracker/issues/ with 40 chars.
        return filter(lambda x: len(x) == 40, os.listdir(self.paths['issues']))
