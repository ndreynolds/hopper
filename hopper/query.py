"""Run queries on an issue database"""

from hopper.database import Database
from hopper.issue import Issue
from sqlalchemy.sql import asc, desc

class Query(object):
    """
    Query objects have methods to query the tracker they are initialized with.
    Queries are performed against either the SQLite db or the JSON file db,
    depending on availability and performance. 

    :param tracker: Tracker object to perform queries on.
    """
    def __init__(self, tracker):
        self.tracker = tracker
        self.has_db = True
        if self.has_db:
            self.db = Database(self.tracker, check=False)
            self.table = self.db.issues

    def select(self, order_by='updated', status='open', label=None, limit=None, 
               offset=None, reverse=True):
        """
        Return issues, with options to limit, offset, sort, and filter the result set.

        :param order_by: order the results by this column.
        :param status: return results with this status.
        :param limit: maximum number of results to return.
        :param offset: skip the first n-results. 
        :param reverse: results are returned in ascending order if True, 
                        descending if False.
        """ 
        if self.has_db:
            order = asc if reverse else desc
            query = self.db.select(order_by=order(order_by), limit=limit, offset=offset)
            query = query.where(self.table.c.status == status)
            if label:
                query = query.where(self.table.c.labels.like('%' + label + '%'))
            rows = query.execute()
            issues = [Issue(self.tracker, r['id']) for r in rows]
        else:
            issues = [Issue(self.tracker, sha) for sha in self.tracker._get_issue_shas()]
            issues.sort(key=lambda x: getattr(x, order_by), reverse=reverse)
            offset = 0 if offset is None else offset
            if limit is not None:
                issues = issues[offset:(offset + limit)]
            else:
                issues = issues[offset:]
        return issues

    def search(self, sstr, status=None, n=20):
        """
        Return issues whose title, content, or comments contain the search
        string.
        
        :param sstr: search string, the string to query the database for.
        :param status: if not None, search only issues with the given status.
        :param n: the number of issues.
        """
        if self.has_db:
            sstr = '%' + sstr + '%'
            rows = self.db.conn.execute("""
                                        SELECT * FROM issues WHERE
                                           title    LIKE ? OR
                                           content  LIKE ? OR
                                           comments LIKE ?
                                        """, (sstr, sstr, sstr))
            rows = rows.fetchmany(n)
            return [Issue(self.tracker, r['id']) for r in rows]
        else:
            raise NotImplementedError

    def count(self, status=None):
        """
        Return the number of issues.

        :param status: if not None, return the count of issues with this status.
        """
        if status is None:
            return len(self.tracker._get_issue_shas())
        else:
            query = self.db.select().where(self.table.c.status==status)
            result = query.count().execute()
            return result.fetchone()[0]
