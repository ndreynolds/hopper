import unittest
from hopper.test_env import TestEnv

class ModuleTest(unittest.TestCase):
    def setUp(self):
        self.env = TestEnv()
        self.tracker = self.env.tracker

    def tearDown(self):
        self.env.cleanup()

if __name__ == '__main__':
    unittest.main()
