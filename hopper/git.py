from __future__ import with_statement
import os
import subprocess

from dulwich.repo import Repo as DulwichRepo
from dulwich.objects import Commit, Blob, Tree

class Repo(object):
    '''
    An abstraction layer that sits on top of Dulwich to provide high-level 
    Git repository interaction.

    In some places this is purely a wrapper of dulwich.Repo, in others
    it uses low-level dulwich methods to achieve high-level ends emulating
    the common git commands (e.g. add, commit, branch, log).

    The underlying dulwich Repo object can always be accessed through
    Repo.repo (as redundant as that is).

    This should be considered a work-in-progress, and as such, a lot 
    of it doesn't work yet.
    '''

    def __init__(self, path):
        self.repo = DulwichRepo(path) # The inner Dulwich Repo object.
        self.root = path

    @classmethod
    def init(cls, path, mkdir=False, bare=False):
        '''
        Initializes a normal or bare repository. This is mostly a
        handoff to Dulwich.
        
        :param path: the path (which must be a directory) to create
                     the repository within.
        :param mkdir: if True, make a directory at **path**. Equivalent 
                      to ``mkdir [path] && cd [path] && git init``.
        :param bare: if True, create a bare repository at the path.

        :return: a ``Repo`` instance.
        '''
        if bare:
            DulwichRepo.init_bare(path)
        else:
            DulwichRepo.init(path, mkdir)
        return cls(path)

    def add(self, path=None, all=False):
        '''
        Add files to the repository or staging area. Equivalent to 
        the `git add` command. 

        :param path: the path to the file to add.
        :param all: if True, add all files under the given path. If 
                    **path** is omitted, the repository's root path 
                    will be used.

        :return: list of filepaths that were added.
                   
        If **path** is a file and **all** is True, only the single 
        file will be added.
        If **path** is a directory and **all** is False, nothing 
        will be added.
        Likewise, if both **path** and **all** are omitted, nothing 
        will be added.        
        '''

        # the implementation creates a list of paths and stages them using 
        # dulwich.Repo.stage

        adds = []

        # add all files within given path
        if path is not None and all:
            if os.path.isdir(path):
                # walk the directory
                for directory, dirnames, filenames in os.walk(directory):
                    if '.git' in dirnames:
                        # in case path is root, don't traverse the .git subdir 
                        dirnames.remove('.git')
                    for f in filenames:
                        path = os.path.join(directory, f)
                        adds.append(path)
            elif os.path.isfile(path):
                adds.append(path)
        
        # add all files within root path
        elif path is None and all:
            # walk the root directory
            for directory, dirnames, filenames in os.walk(self.root):
                if '.git' in dirnames:
                    # don't traverse the .git subdir 
                    dirnames.remove('.git')
                for f in filenames:
                    path = os.path.join(directory, f)
                    adds.append(path)

        # add file at path
        elif path is not None:
            # add only if file
            if os.path.isfile(path):
                adds.append(path)

        # make sure we've got relpaths, otherwise Dulwich will freak.
        rels = []
        for p in adds:
            # get the relpath relative to repo root.
            rels.append(os.path.relpath(p, self.root))
        adds = rels

        # don't waste time with stage if empty list.
        if adds:
            self.repo.stage(adds)

        return adds

    def branch(self, name=None, commit=None):
        '''
        Create a new branch or display the current one. Equivalent to 
        `git branch`.
        
        :param name: the name of the branch
        :param commit: a commit identifier. Same idea as the ``--start-point``
                       option. Will create the branch off of the commit. 
                       Defaults to HEAD.
        '''
        # create a branch
        if name is not None:
            if commit is None:
                commit = self.head().id
            self.repo.refs['refs/heads/%s' % name] = commit
        # display the current branch
        else:
            # couldn't find an easy way to get it out of dulwich, so we'll
            # just read the HEAD file directly.
            path = os.path.join(self.repo._controldir, 'HEAD')
            if os.path.isfile(path):
                with open(path, 'r') as fp:
                    return fp.read().strip()

    def checkout(self, identifier):
        '''
        Checkout a branch, commit, or file.
        '''
        raise NotImplementedError

    def cmd(self, cmd):
        '''
        Run a raw git command from the shell and return any output. Unlike 
        other methods (which depend on Dulwich's git reimplementation and 
        not git itself), this is dependent on the git shell command. 

        The given command and arguments are prefixed with:

        ``git --git-dir=[/path/to/tracker/.git] --work-tree=[/path/to/tracker]``

        and run through the ``subprocess.Popen`` method.

        :param cmd: A list of command-line arguments (anything the subprocess 
                    module will take).
        :return: a string containing the command's output.

        **Usage** (output has truncated for brevity):
          >>> Repo.cmd(['checkout', '-q', 'master'])
          >>> Repo.cmd(['commit', '-q', '-a', '-m', 'Initial Commit'])
          >>> Repo.cmd(['remote', '-v'])
          "origin  git@ndreynolds.com:hopper.git (fetch)\\n\\n origin ..."
          >>> Repo.cmd(['log'])
          "commit 68a116eaee458607a3a9cf852df4f358a02bdb92\\nAuthor: Ni..."

        As you can see, it doesn't do any parsing of the output. It's available
        for times when the other methods don't get the job done.
        '''

        if not type(cmd) is list:
            raise TypeError('cmd must be a list')
        git_dir = os.path.join(self.root, '.git')
        prefix = ['git', '--git-dir', git_dir, '--work-tree', self.root]
        # It would be nice to use check_output() here, but it's 2.7+
        return subprocess.Popen(prefix + cmd, stdout=subprocess.PIPE).communicate()[0]

    def commit(self, all=False, **kwargs):
        '''
        Commit the changeset to the repository.  Equivalent to the 
        `git commit` command.

        This method does a commit; use the ``commits`` method to 
        retrieve one or more commits.

        Uses ``dulwich.objects.BaseRepo.do_commit()``, see that for
        params. At minimum, you need to provide **committer** and 
        **message**. Everything else will be defaulted.

        :param all: commit all modified files that are already being tracked.
        :param **kwargs: the commit attributes (e.g. committer, message,
                         etc.). Again, see the underlying dulwich method.
        '''
        
        if all:
            self.add(all=True)

        # pass the kwargs to dulwich, get the returned commit id.
        commit_id = self.repo.do_commit(**kwargs)

        # return the Commit object (instead of the id, which is less useful).
        return self.commits(commit_id)

    def commits(self, identifier=None, n=10):
        '''
        Return one or more commits from an identifier, or if omitted,
        up to n-commits down from the HEAD.

        :param identifer: a branch (not yet) or SHA. Given a SHA, the
                          return value will be a single Commit object.
                          Anything else gets you a list.
        :param n: the maximum number of commits to return. If fewer 
                  matching commits exist, only they will be returned.
        '''

        # eventually this needs to check if the identifier is a branch
        # or tag first, then look for an identifier.

        if identifier is not None:
            return self.repo[identifier]
        return self.repo.revision_history(self.head().id)[:n]

    def diff(self, a, b=None, path=None):
        '''
        Return a diff of commits a and b.

        :param a: a commit identifier.
        :param b: a commit identifier. Defaults to HEAD.
        :param path: a path to a file or directory to diff. Defaults
                     to the entire tree.
        '''
        raise NotImplementedError

    def head(self):
        '''
        Return the HEAD or raise an error.
        '''

        # It seems best to make this a function so we don't have to
        # set and continually update it.
        try:
            return self.repo['HEAD']
        except KeyError:
            # The HEAD will be missing before the repo is committed to.
            raise NoHeadSet

    def log(self):
        return self.commits()

    def tag(self, sha):
        return self.repo.tag(sha)

    def tree(self, sha):
        return self.repo.tree(sha)

class NoHeadSet(Exception):
    '''The repository has no HEAD.'''
