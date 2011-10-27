from __future__ import with_statement
import os
import glob

from hopper.git import Repo
from hopper.issue import Issue
from hopper.utils import match_path
from hopper.config import TrackerConfig
from hopper.document import Document
from hopper.query import Query
from hopper.database import Database

class Tracker(object):
    """
    Defines a Hopper tracker and provides paths to files within a 
    tracker. 

    :param path: the relative or absolute path to the tracker
    """
    def __init__(self, path):
        if not os.path.exists(path):
            path = match_path(path)
            if path is None:
                raise OSError('Supplied path does not exist')

        # remove trailing slash
        if path.endswith('/'):
            path = path[:-1]

        self.path = path
        self.paths = {
                'root'  : self.path,
                'base'  : os.path.basename(self.path),
                'config': os.path.join(self.path, 'config'),
                'issues': os.path.join(self.path, 'issues'),
                'admin': os.path.join(self.path, '.hopper'),
                'docs'  : os.path.join(self.path, 'docs')
                }
        self.properties = {
                'name': None
                }
        self.repo = Repo(path)
        self.config = TrackerConfig(self)
        self.db = Database(self)

    @classmethod
    def new(cls, path):
        """
        Create and return tracker at the given path.

        :param path: path to create the directory at. For example,
                     supplying ``my_tracker`` would create the directory
                     ``./my_tracker``.
        """
        # remove trailing slash
        if path.endswith('/'):
            path = path[:-1]

        # set the install paths
        paths = {
                'root'  : path,
                'issues': os.path.join(path, 'issues'),
                'admin' : os.path.join(path, '.hopper'),
                'docs'  : os.path.join(path, 'docs')
                }

        # create the repository
        repo = Repo.init(paths['root'], mkdir=True)

        # build the default structure
        open(os.path.join(paths['root'], 'config'), 'w').close()
        os.mkdir(paths['issues'])
        open(os.path.join(paths['issues'], 'empty'), 'w').close()
        os.mkdir(paths['admin'])
        open(os.path.join(paths['admin'], 'empty'), 'w').close()
        os.mkdir(paths['docs'])

        # read sample docs from packaged `templates` into `docs`.
        templates = os.path.join(os.path.dirname(__file__), 'templates')
        for p in os.listdir(templates):
            with open(os.path.join(templates, p), 'r') as fp:
                data = fp.read()
            with open(os.path.join(paths['docs'], p), 'w') as fp:
                fp.write(data)

        # set the config
        config = TrackerConfig(cls(path))
        config.name = os.path.basename(path).capitalize()
        config.save()

        # add everything to the repo and commit
        repo.add(all=True)
        repo.commit(committer='Hopper <hopper@hopperhq.com>',
                    message='Created the %s tracker' % config.name)

        # instantiate and return our new Tracker.
        return cls(path)

    def autocommit(self, message, author=None):
        """
        Commit any changes to the repo. In most scenarios, the user
        responsible for the change(s) would be listed as the commit 
        author, and Hopper would be the committer.  

        :param msg: the commit message to use.
        :param author: the commit's author in string or dictionary
            format. For example: ``'Full Name <your.email@domain.tld>'``
            **or** ``{'name': 'Full Name', 'email': 'your.email@domain.tld'}``
        :return: the Commit object.
        """
        committer = 'Hopper <hopper@hopperhq.com>'

        if type(author) is dict:
            author = '%s <%s>' % (author['name'], author['email'])
        if type(author) is not str:
            author = committer

        self.repo.add(all=True)
        return self.repo.commit(message=message, committer=committer,
                                author=author)

    def doc(self, path):
        """
        Return the document at the path.

        :param path: a path relative to the tracker's `docs` directory.
        """
        matches = glob.glob(os.path.join(self.paths['docs'], path) + '*')
        if not matches:
            raise OSError('Document does not exist')
        match = os.path.relpath(matches[0], self.paths['docs'])
        return Document(self, match)

    def docs(self):
        """Return a list of Document objects."""
        return [Document(self, path) for path in os.listdir(self.paths['docs'])]

    def read(self, relpath, mode='r'):
        """
        Read a file relative to the tracker root.

        :param relpath: a path relative to the tracker's root directory.
        :param mode: the file mode to use (e.g. 'r' or 'wb').
        """
        path = os.path.join(self.paths['root'], relpath)
        with open(path, mode) as fp:
            return fp.read()

    def issue(self, sha):
        """
        Return the Issue object with the given SHA1.
        
        :param sha: the issue's SHA1 identifier.
        """
        return Issue(self, sha)

    def issues(self, n=None, offset=0, sort_by='updated', reverse=True, 
               return_num=False, conditions=None):
        """
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
        """
        query = Query(self)
        return query.select(limit=20, offset=None)

    def history(self, n=10, all=False):
        """
        Return a list of dictionaries containing the action and the actor.
        These are assembled from the Git repository's commit log.

        :param n: the maximum number of history items to return.
        :param all: ignore n and return everything.
        """
        if all:
            return self.repo.commits()
        return self.repo.commits()[:n]

    def get_issue_path(self, sha):
        """
        Returns the absolute path to the issue. It doesn't check if the issue
        exists; this should be done afterwards if necessary.

        :param sha: the issue's unique identifier.
        """
        return os.path.join(self.paths['issues'], sha, 'issue')

    def query(self):
        """
        Returns a hopper.query.Query object for querying the issue 
        database.
        """
        return Query(self)

    def _get_issues(self):
        """Returns a list of all issue objects."""
        return [Issue(self, sha) for sha in self._get_issue_shas()]

    def _get_issue_shas(self):
        """Return a list of the SHA1s of all issues in the tracker."""
        # we'll just return any paths in tracker/issues/ with 40 chars.
        # since we're not verifying, this may not be 100% accurate.
        return filter(lambda x: len(x) == 40, os.listdir(self.paths['issues']))
