import unittest
import os

from env import TestEnv
from hopper.tracker import Tracker
from hopper.database import SQLiteIssueDatabase, IssueQuery
from hopper.issue import Issue
from sqlalchemy.sql import Select

class IssueQueryTest(unittest.TestCase):
    '''Tests the `IssueQuery` class.'''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__get_issue_shas(self):
        '''Tests the `_get_issue_shas` method'''
        pass

    def test_count(self):
        '''Tests the `count` method'''
        pass

    def test_search(self):
        '''Tests the `search` method'''
        pass

    def test_select(self):
        '''Tests the `select` method'''
        pass


class SQLiteIssueDatabaseTest(unittest.TestCase):
    '''Tests the `SQLiteIssueDatabase` class.'''

    def setUp(self):
        self.env = TestEnv()

    def tearDown(self):
        self.env.cleanup()

    def test_constructor(self):
        '''Test the __init__ method.'''
        path = os.path.join(self.env.tracker.paths['admin'],
                            'cache', 'tracker.db')

        # Init a database when one does not exist:
        db1 = SQLiteIssueDatabase(self.env.tracker)
        assert os.path.exists(path)
        assert db1.conn

        # Init a database when one already exists:
        db2 = SQLiteIssueDatabase(self.env.tracker)
        assert os.path.exists(path)
        assert db2.conn

    def test__apply_working_tree(self):
        '''Tests the `_apply_working_tree` method'''
        pass

    def test__insert_many_from_shas(self):
        '''Tests the `_insert_many_from_shas` method'''
        pass

    def test__integrity_check(self):
        '''Tests the `_integrity_check` method'''
        pass

    def test__replicate(self):
        '''Tests the `_replicate` method'''
        pass

    def test__set_update(self):
        '''Tests the `_set_update` method'''
        pass

    def test_insert(self):
        '''Tests the `insert` method'''
        db = SQLiteIssueDatabase(self.env.tracker)
        # make and insert the issue
        issue1 = Issue(self.env.tracker)
        issue1.content = 'test'
        issue1.title = 'Test'
        issue1.save()
        db.insert(issue1)
        rows = db.select().execute()
        issue2 = [Issue(self.env.tracker, r['id']) for r in rows][0]
        # make sure the issues are equal which triggers the __eq__ method.
        assert issue1 == issue2

    def test_insert_many(self):
        '''Tests the `insert_many` method'''
        db = SQLiteIssueDatabase(self.env.tracker)
        issues = []
        for i in range(20):
            issue = Issue(self.env.tracker)
            issue.save()
            issues.append(issue)
        db.insert_many(issues)
        rows = db.select().execute()
        db_issues = [Issue(self.env.tracker, r['id']) for r in rows]
        # quick check to make sure they're all there.
        assert len(db_issues) == len(issues)

    def test_select(self):
        '''Tests the `select` method'''
        db = SQLiteIssueDatabase(self.env.tracker)
        # should just return an sqlalchemy.sql.Select object.
        assert type(db.select()) is Select


if __name__ == '__main__':
    unittest.main()
