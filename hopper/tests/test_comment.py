import unittest
from hopper.test_env import TestEnv
from hopper.comment import Comment
from hopper.issue import Issue

class CommentTest(unittest.TestCase):
    def setUp(self):
        self.env = TestEnv()
        self.tracker = self.env.tracker
        self.issue = Issue(self.tracker)

    def tearDown(self):
        self.env.cleanup()

    def test_read(self):
        c1 = Comment(self.issue)
        c1.content = 'red'
        c1.save()
        c2 = Comment(self.issue)
        c2.content = 'blue'
        c2.save()
        c2.read(c1.id)
        assert c2.fields == c1.fields

    def test_save(self):
        pass

    def test_save_issue(self):
        pass

    def test_delete(self):
        pass

    def test_rm(self):
        pass

if __name__ == '__main__':
    unittest.main()
