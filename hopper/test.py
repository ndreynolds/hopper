from tracker import Tracker
from issue import Issue
from comment import Comment

tracker = Tracker.create('new_tracker')
issue1 = Issue(tracker)
issue1.title = 'test'
issue1.save()

issue1 = Issue(tracker, issue1.id)
comment = Comment(issue1)
comment.content = 'hey there'
comment.add()
issue1.save()
print issue1.id
