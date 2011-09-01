from __future__ import with_statement
import os
import time

from dulwich.repo import Repo as DulwichRepo
from dulwich.objects import Commit as DulwichCommit
from dulwich.objects import Blob, Tree

class Repo(object):
    '''High-level Git interactions using Dulwich.'''

    def __init__(self, path):
        self.repo = DulwichRepo(path)
        self._set_head()
        self.tree = Tree()
        self.blobs = []
        self.root = path

    @classmethod
    def init(cls, path, mkdir=False, bare=False):
        '''Initializes a normal or bare repository.'''
        if bare:
            DulwichRepo.init_bare(path)
        else:
            DulwichRepo.init(path, mkdir)
        return cls(path)

    def add_all(self, directory=None):
        '''
        Mimics the `git add .` command.

        If :directory is supplied, stage all files within that directory 
        (recursively). :directory defaults to the repo root.  
        '''
        if directory is None:
            directory = self.root
        if not os.path.isdir(directory):
            return False
        for directory, dirnames, filenames in os.walk(directory):
            if '.git' in dirnames:
                # don't traverse the .git subdir
                dirnames.remove('.git')
            for f in filenames:
                self._add_to_tree(os.path.join(directory, f))

    def add(self, path):
        '''
        Mimics the `git add <file>` command.

        :param path: the path to the file to add.
        '''
        self._add_to_tree(path)

    def branch(self, name, head=None):
        '''Create a new branch with the given name.'''
        if head is None:
            head = self.head.id
        self.repo.refs['refs/heads/%s' % name] = head

    def commit(self, **kwargs):
        '''
        Mimics the `git commit` command.

        The commit method will accept any arguments accepted by 
        Dulwich's Repo.commit(). It merges these arguments with some
        sensible defaults. For example, commit_time will be handled
        automatically. 

        Not all arguments have sensible defaults. At minimum you 
        should provide:

            :param message: the commit message
            :param author: the commit author
        '''
        defaults = {
                'commit_time': int(time.time()),
                'commit_timezone': 0,
                'encoding': 'UTF-8',
                'parents': [],
                'tree': self.tree.id
                }

        options = dict(defaults.items() + kwargs.items())
        if not options.has_key('author_time'):
            options['author_time'] = options['commit_time']
        if not options.has_key('author_timezone'):
            options['author_timezone'] = options['commit_timezone']
        if not options.has_key('committer'):
            options['committer'] = options['author']
        commit = DulwichCommit()
        # Set the commit attributes from the dictionary
        for key in options.keys():
            setattr(commit, key, options[key])
        self.commit = commit
        self._store_objects()
        self.branch('master', commit.id)

    def get_commits(self, n=10, branch=None):
        if not hasattr(self, 'head'):
            raise MissingHead
        return self.repo.revision_history(self.head.id)[:n]

    def get_commit(self, sha):
        return self.repo.commit(sha)

    def log(self):
        return self.get_commits()

    def tag(self, sha):
        return self.repo.tag(sha)

    def tree(self, sha):
        return self.repo.tree(sha)

    def _add_to_tree(self, path):
        '''Create a blob from the given file and add the blob to the tree.'''
        if os.path.isfile(path):
            fname = os.path.split(path)[-1]
            with open(path, 'r') as fp:
                blob_string = fp.read()
            blob = Blob.from_string(blob_string)
            self.blobs.append(blob)
            self.tree.add(fname, 0100644, blob.id)

    def _store_objects(self):
        '''Store the objects in the repo's object store.'''
        if self.blobs:
            obj_store = self.repo.object_store
            for blob in self.blobs:
                obj_store.add_object(blob)
            obj_store.add_object(self.tree)
            obj_store.add_object(self.commit)
            return True
        else:
            print 'Nothing to store.' 
            return False

    def _set_head(self):
        '''Set the repo's head attribute.'''
        if self.repo.head:
            return
        if self.repo.refs.has_key('HEAD'):
            self.head = self.repo.commit(self.repo.head())
            self.head.tree = self.repo.tree(self.head.tree)

class MissingHead(Exception):
    '''The repository has no HEAD'''
