"""SQLite issue database representation."""

from __future__ import with_statement
import os
from sqlalchemy import create_engine, Table, Column, String, Float
from sqlalchemy.schema import MetaData

class Database(object):
    """
    SQLite representation of the tracker's issue database. Handles SQL through
    SQLAlchemy. It also handles syncing with the primary database.

    Why:

    Hopper's primary issue database is a flat-file, with JSON-encoded issue and 
    comment files. This is ideal for versioning, but not for performance. If the 
    tracker has 5000 issues, it has to open and read 5000 files to sort them. 
    That tends to take a while. To improve performance, we can mirror the 
    issues in an SQLite db. Here are the pros and cons of each:
    
    Advantages:

    * Huge performance gains--roughly speaking: O(log n) vs O(n).
    * Repository size doesn't change, as db is not versioned.
    * Get the above advantages without reinventing the wheel.
    * SQLite is installed on most machines already.
    * Non-essential--can be deleted with no consequence.

    Disadvantages:

    * Requires (more than) twice the disk space.
    * Overhead to keep the SQLite db in sync with the flat-file db.

    Syncing:

    To keep in sync, we rely on the Git repository. Next to the db is the 
    ``LAST_UPDATE`` file which contains the HEAD commit at the time of the last
    db modification. Essentially, we're assuming that everything up to that 
    commit is synced.

    Before inserting, if ``LAST_UPDATE != HEAD``, we need to reindex. Even for 
    25000 issues, this should take less than a second. At any rate, this is 
    only an issue after the user does something to change the HEAD (e.g. a pull
    or reset). If the commits are indeed the same, we just apply changes. This 
    just means an ``INSERT OR REPLACE`` or ``DELETE`` for each change.
    """
    def __init__(self, tracker, check=True):
        parent = os.path.join(tracker.paths['admin'], 'cache')
        path = os.path.join(parent, 'tracker.db')
        db = create_engine('sqlite:///%s' % path)
        metadata = MetaData(db)
        issues = Table('issues', metadata,
                Column('id', String, primary_key=True),
                Column('title', String),
                Column('status', String),
                Column('labels', String),
                Column('content', String),
                Column('comments', String),
                Column('created', Float),
                Column('updated', Float),
                Column('author_name', String),
                Column('author_email', String),
                Column('author_avatar', String),
                )
        if not os.path.exists(path):
            if not os.path.exists(parent):
                os.mkdir(parent)
            elif not os.path.isdir(parent):
                raise OSError('Parent path exists, but is not a directory.')
            issues.create()
        self.tracker = tracker
        self.issues = issues
        self.conn = db.connect()
        self.check = check

    def select(self, **kwargs):
        self._integrity_check()
        return self.issues.select(**kwargs)

    def insert(self, issue):
        """
        Insert an Issue object into the database.

        NOTE that the actual SQL statement is an ``INSERT OR REPLACE``.

        :param issue: a single Issue object
        """
        ins = self.issues.insert().prefix_with('OR REPLACE')
        comments = issue.comments()
        # comments just need to be searchable, we're not going to be 
        # retrieving them from this table.
        comment_data = ''.join(c.content for c in comments)
        ins.execute(id=issue.id,
                    title=issue.title,
                    status=issue.status,
                    labels=','.join(issue.labels),
                    content=issue.content,
                    comments=comment_data,
                    created=issue.created,
                    updated=issue.updated,
                    author_name=issue.author['name'],
                    author_email=issue.author['email'],
                    author_avatar=issue.author['avatar']
                    )

    def insert_many(self, issues):
        """
        Insert a list of Issue objects.

        If the number of issues is substantial, ``insert_many_from_shas``
        will perform better.

        :param issues: a list of Issue objects.
        """
        ins = self.issues.insert().prefix_with('OR REPLACE')
        issue_dicts = []
        for i in issues:
            comments = i.comments()
            comment_data = ''.join(c.content for c in comments)
            issue_dicts.append({
                                'id': i.id,
                                'title': i.title,
                                'status': i.status,
                                'labels': ','.join(i.labels),
                                'content': i.content,
                                'comments': comment_data,
                                'created': i.created,
                                'updated': i.updated,
                                'author_name': i.author['name'],
                                'author_email': i.author['email'],
                                'author_avatar': i.author['avatar']
                               })
        if issue_dicts:
            ins.execute(issue_dicts)

    def _insert_many_from_shas(self, shas, n=50):
        """
        Insert issues, given a list of SHA identifiers, as efficiently as
        possible.

        Given 1000+ issues, it may not be feasible to keep all the objects in
        memory. This method will instantiate them as issues and insert them
        in groups of n. For a test case of 25000 issues, groups of 50 were
        optimal; this is the default.

        :param shas: a list of SHA identifiers as strings.
        :param n: group size
        """
        # TODO: n should probably be calculated based on len(shas)
        for i in xrange(0, len(shas), n):
            edge = i + n if i + n < len(shas) else len(shas)
            issues = [self.tracker.issue(shas[j]) for j in range(i, edge)]
            self.insert_many(issues)

    def _set_update(self):
        path = os.path.join(self.tracker.paths['admin'], 'cache', 'LAST_UPDATE')
        with open(path, 'w') as fp:
            fp.write(self.tracker.repo.head().id)

    def _integrity_check(self):
        """
        Check the database for consistency with the JSON database.

        Compares the repo HEAD with the LAST_UPDATE file, and checks the working
        tree. If the commits differ, we do a full replication. If the commits are
        the same, we apply any changes in the working tree.

        Speed is better than accuracy here, so it doesn't provide guarantees.
        If the database has been manually changed, or the Git repository has been
        tampered with, there may be inconsistencies. If we need to be certain, it
        ends up being faster to just replicate. 
        """
        if not self.check:
            return

        path = os.path.join(self.tracker.paths['admin'], 'cache', 'LAST_UPDATE')
        # No marker, must replicate
        if not os.path.exists(path):
            self._replicate()
            return

        # Get some info
        head = self.tracker.repo.head().id
        last_update = open(path, 'r').read()
        dirty = self.tracker.repo.is_dirty()

        # Commits match, but repo is dirty:
        if last_update == head and dirty:
            self._apply_working_tree()
        # (If commits match and repo is clean, nothing happens.)

        # Commits don't match:
        elif last_update != head:
            self._replicate()

    def _replicate(self):
        """Do a full replication of the JSON database into this one."""
        shas = self.tracker._get_issue_shas()
        self._insert_many_from_shas(shas)
        self._set_update()

    def _apply_working_tree(self):
        """Apply changes from the working to the database."""
        # get modified files within issues
        new, modified, deleted = self.tracker.repo.status('issues')
        for path in new + modified:
            # insert or replace row
            sha = path.split(os.sep)[1]
            issue = self.tracker.issue(sha)
            self.insert(issue)
        for path in deleted:
            # delete row
            sha = path.split(os.sep)[1:]
            query = self.issues.delete().where(id=sha)
            query.execute()
