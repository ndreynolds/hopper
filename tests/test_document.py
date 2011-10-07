from __future__ import with_statement
import unittest
import os
from hopper.document import Document
from env import TestEnv

class DocumentTest(unittest.TestCase):
    '''Tests the `Document` class.'''

    def setUp(self):
        self.env = TestEnv()
        self.tracker = self.env.tracker

    def tearDown(self):
        self.env.cleanup()

    def test_constructor(self):
        # create a document called 'test'
        path = os.path.join(self.tracker.paths['docs'], 'test')
        with open(path, 'w') as fp:
            fp.write('test')

        # try to initialize the doc
        Document(self.tracker, 'test')

    def test_read(self):
        '''Tests the `read` method'''
        pass

    def test_write(self):
        '''Tests the `write` method'''
        pass


if __name__ == '__main__':
    unittest.main()
