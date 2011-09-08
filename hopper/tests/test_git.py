from __future__ import with_statement
import unittest
import shutil
import os

from hopper.utils import get_uuid
from hopper.git import Repo
from dulwich.objects import Commit

class RepoTest(unittest.TestCase):
    def setUp(self):
        # a path for the repos
        self.path = get_uuid()

    def tearDown(self):
        # rm -r them afterwards
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)

    def _make_repo_with_commit(self):
        '''Returns a repo with a single commit (of some randomly generated files).'''
        r = Repo.init(self.path, mkdir=True)
        # write some SHAs to a few files
        for i in range(4):
            with open(os.path.join(r.root, 'spam-%d' % i), 'w') as fp:
                fp.write(get_uuid())
        # add the changes
        r.add_all()
        # commit the changes
        r.commit(author='Joe Sixpack', message='Initial commit')
        return r

    def test_init(self):
        # NOTE init is not __init__, but a @classmethod for creating 
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
        assert r2.head == None

    def test_add_all(self):
        pass

    def test_add(self):
        pass

    def test_branch(self):
        pass

    def test_commit(self):
        r = Repo.init(self.path, mkdir=True)
        with open('spam', 'w') as fp:
            fp.write('test')
        r.add('spam')
        c = r.commit(author='GOB Bluth', message='Come on!')
        # make sure the commit got set right
        assert type(c) is Commit
        assert c.author == 'GOB Bluth'
        assert c.message == 'Come on!'
        # the commit should be the same as the Repo.head
        assert c == r.head

    def test_commits(self):
        r = self._make_repo_with_commit()
        # giving it a SHA should return a single Commit object
        assert type(r.commits(r.head.id)) is Commit

    def test_log(self):
        pass

    def test_tag(self):
        pass

    def test_tree(self):
        pass

    def test__add_to_tree(self):
        pass

    def test__store_objects(self):
        pass

    def test__set_head(self):
        pass

if __name__ == '__main__':
    unittest.main()
