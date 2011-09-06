import unittest
import os

from hopper.test_env import TestEnv
from hopper.issue import Issue

class TestIssue(unittest.TestCase):
    def setUp(self):
        self.env = TestEnv()
        self.tracker = self.env.tracker

    def tearDown(self):
        self.env.cleanup()

    def test_setattr(self):
        issue = Issue(self.tracker)
        issue.title = 'test title'
        # Does the __setattr__ method work?
        # i.e.: setting issue.title shoud set issue.fields['title']
        assert issue.title == issue.fields['title']

    def test_getattribute(self):
        issue = Issue(self.tracker)
        issue.fields['title'] = 'test title'
        # Does the __getattribute__ method work?
        # i.e.: issue.title should return issue.fields['title'] 
        assert issue.fields['title'] == issue.title

    def test_read(self):
        issue1 = Issue(self.tracker)
        issue1.title = 'test title'
        issue1.save()
        issue2 = Issue(self.tracker)
        issue2.title = 'different title'
        issue2.read(issue1.id)
        # issue2 should become a clone of issue1 after calling read().
        assert issue1.fields ==  issue2.fields

    def test_save(self):
        issue = Issue(self.tracker)
        issue.title = 'test title'
        issue.save()

        # Get the path to the issue and assert that it's there.
        path = self.tracker.get_issue_path(issue.id)
        assert os.path.exists(path)

        # Does the issue initialized from file match the original?
        issue_clone = Issue(self.tracker, issue.id)
        assert issue_clone.fields == issue.fields

    def test_timestamps(self):
        issue = Issue(self.tracker)
        issue.title = 'test title'
        issue.save()
        assert issue.created == issue.updated
        
if __name__ == '__main__':
    unittest.main()
