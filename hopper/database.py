import os
from sqlalchemy import create_engine, Table, Column, String, Float
from sqlalchemy.schema import MetaData

class IssueDatabase(object):
    '''
    SQLite representation of the tracker's issue database. Relies on SQLAlchemy
    for all the heavy-lifting.

    Hopper's primary issue database is made up of JSON-encoded issue and comment
    files. If the tracker has 5000 issues, it has to open and read 5000 files to
    sort them. This presents a lot of performance issues. Rather than some custom
    indexing scheme, we just mirror the issues in an SQLite db. Using the db is
    optional and as transparent as possible.

    To keep in sync, we rely on the Git repository. Next to the db is the 
    `LAST_UPDATE` file which contains the HEAD commit at the time of the last
    db modification. If the current HEAD and the one in that file differ, we'll
    get the changes, then update and delete accordingly.
    '''
    def __init__(self, tracker):
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
        self.issues = issues

    def save(self, issue):
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

class MiniTracker(object):
    def __init__(self):
        paths = {}
        paths['admin'] = '/home/ndreynolds/repos/hopper/hopper/'
        self.paths = paths

tracker = MiniTracker()
db = IssueDatabase(tracker)
