import unittest
import os

from hopper.test_env import TestEnv
from hopper.tracker import Tracker
from hopper.issue import Issue
from hopper.utils import get_uuid
from hopper.errors import DoesNotExist

class TrackerTest(unittest.TestCase):
    def setUp(self):
        # a random path to init trackers at
        self.path = get_uuid() 
        self.env = TestEnv(False)

    def tearDown(self):
        # delete the tracker at self.path
        if os.path.exists(self.path):
            self.env.rm_tracker(self.path)

    def test_constructor(self):
        # supplying non-existent paths should raise OSError
        try:
            Tracker(self.path)
        except OSError:
            pass

        # supplying a valid path should work.
        t1 = Tracker.new(self.path)
        t2 = Tracker(t1.paths['root'])
        assert type(t2) is Tracker

    def test_new(self):
        # verify that new() returns a Tracker object.
        t = Tracker.new(self.path)
        assert type(t) is Tracker

        # verfify that the tracker was created on disk.
        assert os.path.isdir(t.paths['root'])

    def test_read(self):
        # stub
        pass

    def test_update(self):
        # stub
        pass

    def test_issue(self):
        t = Tracker.new(self.path)
        i1 = Issue(t)
        i1.save()
        i2 = t.issue(i1.id)
        # verify that issue() returns an Issue
        assert type(i2) is Issue
        # verify that the issues match
        assert i1.fields == i2.fields

        # invalid SHAs should raise DoesNotExist
        invalid_sha = get_uuid()
        try:
            t.issue(invalid_sha)
        except OSError:
            pass
        
    def test_issues(self):
        t = Tracker.new(self.path)
        # make a bunch of issues
        issues = [Issue(t) for i in range(50)]


    def test_get_issue_path(self):
        pass

    def test_get_issues(self):
        pass


if __name__ == '__main__':
    unittest.main()
