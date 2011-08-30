from tracker import Tracker
from issue import Issue
from comment import Comment

tracker = Tracker('new_tracker')
issue1 = Issue(tracker)
issue1.title = 'test'
issue1.save()

issue1 = Issue(tracker, issue1.id)
comment = Comment(issue1)
comment.content = 'hey there'
comment.add()
x = comment.id
issue1.save()
print issue1.fields['comments']
print issue1.comments
Comment.rm(issue1, x)
issue1.save()
print issue1.fields['comments']
print issue1.comments

print tracker.issues()
