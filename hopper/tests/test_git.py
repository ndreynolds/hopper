from __future__ import with_statement
import unittest
import shutil
import os

from hopper.utils import get_uuid
from hopper.git import Repo, NoHeadSet
from dulwich.objects import Commit

class RepoTest(unittest.TestCase):
    def setUp(self):
        # a path to create each test case's repo at.
        self.path = get_uuid()

    def tearDown(self):
        # ``rm -r`` self.path afterwards, if exists.
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)

    def _repo_with_commits(self, num_commits=1):
        '''Returns a repo with one or more commits.'''
        r = Repo.init(self.path, mkdir=True)
        for c in range(num_commits):
            for i in range(4):
                with open(os.path.join(r.root, 'spam-%d' % i), 'w') as fp:
                    fp.write(get_uuid())
            # add the files/changes
            r.add(all=True)
            # commit the changes
            r.commit(committer='Joe Sixpack', message='Commit %d' % c)
        return r

    def test_init(self):
        # NOTE init refers not to __init__, but the @classmethod for creating 
        # repositories. See test_constructor() for __init__.

        r = Repo.init(self.path, mkdir=True)

        # make sure it created something.
        assert os.path.isdir(self.path)

        # does the dir have a .git?
        assert os.path.isdir(os.path.join(self.path, '.git'))

        # make sure it returns a Repo object.
        assert type(r) is Repo

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

    def test_add(self):
        pass

    def test_branch(self):
        r = self._repo_with_commits()

        # test repo should be on master branch.
        assert r.branch() == 'ref: refs/heads/master'

        # create new branch (from HEAD)
        r.branch('test_branch')

        # is the branch there? does it resolve to the HEAD's commit id?
        assert r.repo.refs['refs/heads/test_branch'] == r.head().id

        # should still be on master (no checkouts)
        assert r.branch() == 'ref: refs/heads/master'

        # create new branch from commit
        #
        # we'll just use HEAD for simplicity's sake, but this time we're
        # supplying a commit.
        r.branch('test_branch2', commit=r.head().id)

        # and do our checks again.
        assert r.repo.refs['refs/heads/test_branch2'] == r.head().id
        assert r.branch() == 'ref: refs/heads/master'

    def test_commit(self):
        r = Repo.init(self.path, mkdir=True)
        with open(os.path.join(r.root, 'spam'), 'w') as fp:
            fp.write('test')
        r.add('spam')
        c = r.commit(committer='GOB Bluth', message='Come on!')

        # make sure the commit got set right
        assert type(c) is Commit
        assert c.author == 'GOB Bluth'
        assert c.message == 'Come on!'

        # the commit should be the same as the Repo.head
        assert c == r.head()

    def test_commits(self):
        r = self._repo_with_commits(20)

        # returns list of Commit objects
        assert type(r.commits()) is list
        assert type(r.commits()[0]) is Commit

        # setting n=20 should get us 20 commits
        assert len(r.commits(n=20)) == 20

        # should accept a SHA
        assert r.commits(r.head().id)
        # should accept a branch name
        assert r.commits('master')
        # should accept a tag
        # (stub)

    def test_tag(self):
        pass

    def test_tree(self):
        pass

if __name__ == '__main__':
    unittest.main()
