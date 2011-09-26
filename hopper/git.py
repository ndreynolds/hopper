from __future__ import with_statement
import os
import subprocess # only used for Repo.cmd()

from dulwich.repo import Repo as DulwichRepo
from dulwich.objects import Blob, Commit, Tree, Tag
from dulwich.errors import NotTreeError, NotCommitError

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

    def add(self, path=None, all=False, add_new_files=True):
        '''
        Add files to the repository or staging area if new or modified. 
        Equivalent to the ``git add`` command. 

        :param path: the path to the file to add.
        :param all: if True, add all files under the given path. If 
                    **path** is omitted, the repository's root path 
                    will be used.
        :param add_new_files: if True, this command will also add new
                              files. Note the default is True--this is 
                              provided for situations 
                              (like ``git commit -a``), where adding
                              new files would be undesirable.

        :return: list of filepaths that were added.
                   
        If **path** is a file and **all** is True, only the single 
        file will be added.
        If **path** is a directory and **all** is False, nothing 
        will be added.
        Likewise, if both **path** and **all** are omitted, nothing 
        will be added.        

        Additionally, the ``add`` method checks to see if the path(s)
        have been modified. We don't want to create new blobs if we 
        don't need them.
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

        # need relpaths, so Git doesn't freak.
        rels = []
        for p in adds:
            # get the path relative to repo root.
            rels.append(os.path.relpath(p, self.root))
        adds = rels

        # filter unmodified files (and untracked files if not add_new_files)
        if add_new_files:
            adds = [f for f in adds if self._file_is_modified(f) or \
                    not self._file_in_tree(f)]
        else:
            adds = [f for f in adds if self._file_is_modified(f)]

        # don't waste time with stage if empty list.
        if adds:
            self.repo.stage(adds)

        return adds

    def branch(self, name=None, commit=None):
        '''
        Create a new branch or display the current one. Equivalent to 
        `git branch`.
        
        :param name: the name of the branch
        :param commit: a commit SHA. Same idea as the ``--start-point``
                       option. Will create the branch off of the commit. 
                       Defaults to HEAD.
        
        When the name param is not given, the current branch will be
        returned as a string in the format: 

            ``ref: refs/heads/[branch_name]``

        Note that this is just the contents of ``.git/HEAD``.
        '''
        # create a branch
        if name is not None:
            if commit is None:
                commit = self.head().id
            self.repo.refs['refs/heads/%s' % name] = commit
        # display the name of the current branch
        else:
            # couldn't find an easy way to get it out of dulwich, 
            # which resolves HEAD to the commit, so we'll just read 
            # .git/HEAD directly.
            path = os.path.join(self.repo._controldir, 'HEAD')
            if os.path.isfile(path):
                with open(path, 'r') as fp:
                    return fp.read().strip()

    def checkout(self, ref, path=None):
        '''
        Checkout the entire tree (or a subset) of a commit given a branch, 
        tag, or commit SHA.

        This is a fairly naive implementation. It will just write the blob data
        recursively from the tree pointed at by the given reference, 
        overwriting the working tree as necessary. It doesn't do deletions or 
        renames.

        If you wanted to checkout 'HEAD':
          >>> repo.checkout(repo.head())

        If you wanted to checkout the master branch:
          >>> repo.checkout('master')

        If you wanted to checkout v1.2 (i.e. a tag):
          >>> repo.checkout('v1.2')

        :param ref: branch, tag, or commit
        :param path: checkout only file or directory at path, should be
                     relative to the repo's root. 
        '''
        sha = self._resolve(ref)
        obj = self.repo[sha]
        tree = self.repo[obj.tree]

        if tree is None:
            raise KeyError('Bad reference: %s' % ref)
        if path is None:
            path = self.root

        else:
            # check if path and self.root are same
            if not os.path.samefile(path, self.root):
                # if not, we need the path's tree 
                # (a sub-tree of the commit tree)
                tree = self._tree_grab(tree, path)
        
        # write the tree
        self._tree_write(tree, path)

    def cmd(self, cmd):
        '''
        Run a raw git command from the shell and return any output. Unlike 
        other methods (which depend on Dulwich's git reimplementation and 
        not git itself), this is dependent on the git shell command. 

        The given git subcommand and arguments are prefixed with ``git`` and
        run through the subprocess module.

        To maintain the class's indifference to the current working directory,
        we also prepend the ``--git-dir`` and ``--work-tree`` arguments. 

        :param cmd: A list of command-line arguments (anything the subprocess 
                    module will take).
        :return: a string containing the command's output.

        **Usage** (output has been truncated for brevity):
          >>> repo.cmd(['checkout', '-q', 'master'])
          >>> repo.cmd(['commit', '-q', '-a', '-m', 'Initial Commit'])
          >>> repo.cmd(['remote', '-v'])
          "origin  git@ndreynolds.com:hopper.git (fetch)\\n\\n origin ..."
          >>> repo.cmd(['log'])
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

    def commit(self, all=False, force=False, **kwargs):
        '''
        Commit the changeset to the repository.  Equivalent to the 
        `git commit` command.

        This method does a commit; use the ``commits`` method to 
        retrieve one or more commits.

        Uses ``dulwich.objects.BaseRepo.do_commit()``, see that for
        params. At minimum, you need to provide **committer** and 
        **message**. Everything else will be defaulted.

        :param all: commit all modified files that are already being tracked.
        :param \*\*kwargs: the commit attributes (e.g. committer, message,
                         etc.). Again, see the underlying dulwich method.
        '''
        
        if all:
            # add all changes (to already tracked files)
            self.add(all=True, add_new_files=False)

        # pass the kwargs to dulwich, get the returned commit id.
        commit_id = self.repo.do_commit(**kwargs)

        # return the Commit object (instead of the id, which is less useful).
        return self.repo[commit_id]

    def commits(self, ref=None, n=10):
        '''
        Return up to n-commits down from a ref (branch, tag, commit),
        or if no ref given, down from the HEAD.

        :param ref: a branch, tag (not yet), or commit SHA to use 
                          as a start point.
        :param n: the maximum number of commits to return. If fewer 
                  matching commits exist, only they will be returned.

        :return: a list of ``dulwich.objects.Commit`` objects.

        **Usage**:
          >>> repo.commits()
          [<Commit 6f50a9bcd25ddcbf21919040609a9ad3c6354f1c>,
           <Commit 6336f47615da32d520a8d52223b9817ee50ca728>]
          >>> repo.commits()[0] == repo.head()
          True
          >>> repo.commits(n=1)
          [<Commit 6f50a9bcd25ddcbf21919040609a9ad3c6354f1c>]
          >>> repo.commits('6336f47615da32d520a8d52223b9817ee50ca728', n=1)
          [<Commit 6336f47615da32d520a8d52223b9817ee50ca728>]
        '''

        start_point = self.head().id
        if ref is not None:
            start_point = self._resolve(ref)

        return self.repo.revision_history(start_point)[:n]

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
        '''Return the HEAD commit or raise an error.'''
        # It seems best to make this a function so we don't have to
        # set and continually update it.
        try:
            return self.repo['HEAD']
        except KeyError:
            # The HEAD will be missing before the repo is committed to.
            raise NoHeadSet

    def log(self):
        # Need to decide if this is necessary.
        # It should do, more or less, the same thing as commits().
        return self.commits()

    def object(self, sha):
        '''
        Retrieve an object from the repository.

        :param sha: the 40-byte hex-rep of the object's SHA1 identifier.
        '''
        return self.repo[sha]

    def tag(self, name, commit=None):
        '''
        Create a tag.

        :param name: name of the new tag (e.g. 'v1.0' or '1.0.6')
        :param commit: a commit SHA to tag, defaults to HEAD.
        '''
        if commit is None:
            commit = self.head().id
        self.repo.refs['refs/tags/%s'] = commit

    def tree(self, sha):
        '''
        Return the tree with given SHA. Raise an error if an object
        matches the SHA, but is not a tree.

        :param sha: tree reference
        '''
        obj = self.repo[sha]
        if type(obj) is Tag:
            return obj
        else:
            raise NotTreeError

    def _file_is_modified(self, path):
        '''
        Returns True if the current file has been modified from the
        blob in the HEAD commit's tree, False otherwise.

        :param path: path to the file relative to the repository root.

        This returns False for new files (not present in the tree). If this
        is unexpected, just call ``_file_in_tree`` first.

        It assumes that the given path does exist. Just expect an OSError
        if it doesn't.
        '''
        # handle no head scenario when this gets called before first commit
        try:
            self.head()
        except NoHeadSet:
            return False

        # get the tree
        tree = self.repo[self.head().tree]
        # get the blob from the tree
        blob1 = self._tree_grab(tree, path)
        if type(blob1) is not Blob:
            return False

        # make a second blob from the current file
        with open(os.path.join(self.root, path), 'r') as fp:
            blob2 = Blob.from_string(fp.read())
        # are the two blobs equivalent? 
        # if their contents are the same they should be...
        # calls dulwich.objects.ShaFile.__eq__, which just compares SHAs
        return blob1 != blob2

    def _file_in_tree(self, path):
        '''
        Returns True if the file corresponds to a blob in the HEAD 
        commit's tree, False otherwise.

        :param path: path to the file relative to the repository root.
        '''
        # handle no head scenario when this gets called before first commit
        try:
            self.head()
        except NoHeadSet:
            return False

        # get the tree
        tree = self.repo[self.head().tree]
        if self._tree_grab(tree, path) is not None:
            return True
        return False

    def _tree_grab(self, tree, path):
        '''
        Walk a Git tree recursively to retrieve and return a blob or 
        sub-tree, or return None if one does not exist.

        :param tree: a dulwich.objects.Tree object.
        :param path: path relative to the repository root. 

        :return: Tree object, Blob object, or None if the path could 
                 not be found.
        
        For example, providing ``hopper/git.py`` would return the 
        ``git.py`` blob within the ``hopper`` sub-tree.
        '''
        if type(tree) is not Tree:
            raise NotTreeError
        # remove trailing slashes from path (so basename doesn't return '')
        if path[-1] == os.sep:
            path = path[:-1]
        parent = os.path.dirname(path)
        basename = os.path.basename(path)
        for entry in tree.iteritems():
            # these are dulwich.objects.TreeEntry objects
            if entry.path == basename:
                # get the Tree or Blob.
                obj = self.repo[entry.sha]
                # return if we're at the right path
                if basename == path:
                    return obj
                # otherwise recurse if it's a Tree
                elif type(obj) is Tree:
                    return self._tree_grab(obj, parent)

        # if we get here the path wasn't there.
        return None

    def _tree_write(self, tree, basepath):
        '''
        Walk a Git tree recursively and write each blob's data to
        disk.

        :param tree: a dulwich.objects.Tree object.
        :param basepath: blob data is written to:
                         ``os.path.join(basepath, blob_path)``.
                         Recursive calls will append the sub-tree
                         name to the original call.
        '''
        if type(tree) is not Tree:
            raise NotTreeError
        for entry in tree.iteritems():
            obj = self.repo[entry.sha]
            if type(obj) is Blob:
                path = os.path.join(basepath, entry.path)
                with open(path, 'wb') as fp:
                    fp.write(obj.data)
            elif type(obj) is Tree:
                new_basepath = os.path.join(basepath, entry.path)
                self._tree_write(obj, new_basepath)

    def _resolve(self, ref):
        '''
        Resolve a reference to a commit SHA.

        :param ref: branch, tag, commit reference.
        :return: a commit SHA.
        :raises KeyError: if ref doesn't point to a commit.

        Branches and tags can have the same shortname. When the ref 
        is ambiguous, Git assumes the branch was meant. This method does
        the same.
        '''
        # order: branch -> tag -> commit
        # (tag and branch can have same name, git assumes branch)

        # dulwich.Repo.refs keys the full name
        # (i.e. 'refs/heads/master') for branches and tags
        branch = _expand_branch_name(ref)
        tag = _expand_tag_name(ref)

        # branch?
        if branch in self.repo.refs:
            # get the commit SHA that the branch points to
            return self.repo[branch].id
        # tag?
        elif tag in self.repo.refs:
            return self.repo[tag].id
        # commit?
        else:
            obj = self.repo[ref]
            if type(obj) is Commit:
                return obj.id
            else:
                raise KeyError('Bad reference: %s' % ref)


def _expand_branch_name(shortname):
    '''Expand branch name'''
    return _expand_ref('heads', shortname)


def _expand_tag_name(shortname):
    '''Expand tag name'''
    return _expand_ref('tags', shortname)


def _expand_ref(ref_type, shortname):
    '''Expand ref shorthand into full name'''
    if shortname.startswith('refs/'):
        return shortname
    if shortname.startswith('%s/' % ref_type):
        return 'refs/%s' % shortname
    return 'refs/%s/%s' % (ref_type, shortname)


class NoHeadSet(Exception):
    '''The repository has no HEAD.'''


class NothingToCommit(Exception):
    '''No changes to the tree.'''
