from __future__ import with_statement
import unittest
import os
import shutil

from hopper.utils import get_uuid
from hopper.git import Repo, NoHeadSet
from dulwich.objects import Commit, Tree
from dulwich.errors import NotTreeError

class NoHeadSetTest(unittest.TestCase):
    '''Tests the `NoHeadSet` class.'''
    pass


class NothingToCommitTest(unittest.TestCase):
    '''Tests the `NothingToCommit` class.'''
    pass


class RepoTest(unittest.TestCase):
    '''Tests the `Repo` class.'''

    def setUp(self):
        # a path to create each test case's repo at.
        self.path = get_uuid()

    def tearDown(self):
        # ``rm -r`` self.path afterwards, if exists.
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)

    def test__apply_to_tree(self):
        '''Tests the `_apply_to_tree` method'''
        pass

    def test__diff_file(self):
        '''Tests the `_diff_file` method'''
        pass

    def test__file_in_tree(self):
        '''Tests the `_file_in_tree` method'''
        pass

    def test__file_is_modified(self):
        '''Tests the `_file_is_modified` method'''
        pass

    def test__resolve(self):
        '''Tests the `_resolve` method'''
        pass

    def test__tree_grab(self):
        '''Tests the `_tree_grab` method'''
        pass

    def test__tree_write(self):
        '''Tests the `_tree_write` method'''
        pass

    def test_add(self):
        '''Tests the `add` method'''
        # TODO - a lot more tests here.
        #
        # Need to verify:
        #   * add path or all
        #   * add only modified
        #   * optionally exclude new files 

        r = self._repo_with_commits()

        def in_index(index, path):
            for i in index.iteritems():
                if i[0] == path:
                    return True
            return False

        # create a new file and add it to index
        # test add path
        self._rand_file('spam-4')
        adds = r.add('spam-4')

        # only 1 file should have been added.
        assert len(adds) == 1

        # is it in the index?
        if not in_index(r.repo.open_index(), 'spam-4'): 
            raise KeyError('File not added to index')

        # create another file
        # test add all
        self._rand_file('spam-5')
        r.add(all=True)

        # is it in the index?
        if not in_index(r.repo.open_index(), 'spam-5'): 
            raise KeyError('File not added to index')

        # unmodified's shouldn't be add-able.
        adds = r.add('spam-0')
        assert len(adds) == 0

        # we want to make sure that the files get committed as well.
        r.commit(message='test', committer='test')
        assert r._file_in_tree('spam-4')
        assert r._file_in_tree('spam-5')

    def test_branch(self):
        '''Tests the `branch` method'''
        r = self._repo_with_commits()

        # test repo should be on master branch.
        assert r.branch() == 'refs/heads/master'

        # create new branch (from HEAD)
        r.branch('test_branch')

        # is the branch there? does it resolve to the HEAD's commit id?
        assert r.repo.refs['refs/heads/test_branch'] == r.head().id

        # should still be on master (no checkouts)
        assert r.branch() == 'refs/heads/master'

        # create new branch from commit
        #
        # we'll just use HEAD for simplicity's sake, but this time we're
        # supplying a commit.
        r.branch('test_branch2', ref=r.head().id)

        # and do our checks again.
        assert r.repo.refs['refs/heads/test_branch2'] == r.head().id
        assert r.branch() == 'refs/heads/master'

    def test_checkout(self):
        '''Tests the `checkout` method'''
        r = self._repo_with_commits(3)

        # we'll checkout the parent of HEAD.
        parent = r.object(r.head().parents[0])
        assert type(parent) is Commit

    def test_cmd(self):
        '''Tests the `cmd` method'''
        pass

    def test_commit(self):
        '''Tests the `commit` method'''
        r = Repo.init(self.path, mkdir=True)
        self._rand_file('spam')
        r.add('spam')

        c = r.commit(committer='GOB Bluth', message='Come on!')

        # make sure the commit got set right
        assert type(c) is Commit
        assert c.author == 'GOB Bluth'
        assert c.message == 'Come on!'

        # the commit should be the same as the Repo.head
        assert c == r.head()

    def test_commits(self):
        '''Tests the `commits` method'''
        r = self._repo_with_commits(20)

        # returns list of Commit objects
        assert type(r.commits()) is list
        assert type(r.commits()[0]) is Commit

        # setting n=20 should get us 20 commits
        assert len(r.commits(n=20)) == 20

        # should accept a SHA
        assert r.commits(r.head().id)
        assert r.commits()[0] == r.head()
        # should accept a branch name
        assert r.commits('master')
        assert r.commits()[0] == r.head()
        # should accept a tag
        assert r.commits('v1.0')
        assert r.commits()[0] == r.head()

    def test_constructor(self):
        r1 = Repo.init(self.path, mkdir=True)

        # verify that an existing repository can be initialized
        r2 = Repo(r1.root)

        # make sure it's a Repo object.
        assert type(r2) is Repo

        # a new repo should have no HEAD
        try:
            r2.head()
        except NoHeadSet:
            pass

    def test_diff(self):
        '''Tests the `diff` method'''
        pass

    def test_head(self):
        '''Tests the `head` method'''
        r = self._repo_with_commits(3)
        head = r.head()
        # make sure it returns a commit
        assert type(head) is Commit
        # in this case, the most recent commit should have the message:
        assert head.message == 'Commit 2'

    def test_init(self):
        '''Tests the `init` method'''
        # NOTE init refers not to __init__, but the classmethod for creating 
        # repositories. See test_constructor() for __init__.

        r = Repo.init(self.path, mkdir=True)

        # make sure it created something.
        assert os.path.isdir(self.path)

        # does the dir have a .git?
        assert os.path.isdir(os.path.join(self.path, '.git'))

        # make sure it returns a Repo object.
        assert type(r) is Repo

    def test_object(self):
        '''Tests the `object` method'''
        pass

    def test_tag(self):
        '''Tests the `tag` method'''
        r = self._repo_with_commits()
        r.tag('test')
        tags_dir = os.path.join(self.path, '.git', 'refs', 'tags')
        assert 'test' in os.listdir(tags_dir)

    def test_tree(self):
        '''Tests the `tree` method'''
        r = self._repo_with_commits()
        # grab the tree from HEAD commit
        t = r.tree(r.head().tree)
        # is it a tree?
        assert type(t) is Tree

        try:
            # giving it a commit id should fail
            t = r.tree(r.head().id)
            # in case it doesn't
            assert type(t) is Tree
        except NotTreeError:
            pass

    def _rand_file(self, path):
        '''Write a SHA1 to a file.'''
        with open(os.path.join(self.path, path), 'w') as fp:
            fp.write(get_uuid())

    def _repo_with_commits(self, num_commits=1):
        '''
        Returns a repo with one or more commits, on master branch, with
        a tag 'v1.0' that points to the last commit.
        '''
        r = Repo.init(self.path, mkdir=True)
        for c in range(num_commits):
            for i in range(4):
                self._rand_file('spam-%d' % i)
            # add the files/changes
            r.add(all=True)
            # commit the changes
            r.commit(committer='Joe Sixpack', message='Commit %d' % c)
        r.tag('v1.0')
        return r


def test__expand_branch_name():
    '''Tests the `_expand_branch_name` function.'''
    pass


def test__expand_ref():
    '''Tests the `_expand_ref` function.'''
    pass


def test__expand_tag_name():
    '''Tests the `_expand_tag_name` function.'''
    pass


if __name__ == '__main__':
    unittest.main()
