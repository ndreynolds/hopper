from flask import Blueprint, render_template, url_for

from hopper.web.utils import setup, looks_hashy
from hopper.utils import relative_time, cut, strip_email
from hopper.errors import BadReference
from hopper.comment import Comment
from hopper.issue import Issue

feed = Blueprint('feed', __name__)

@feed.route('/')
def main():
    tracker, config = setup()
    header = 'Recent Activity for %s' % tracker.config.name
    raw_history = tracker.history(20)
    # get the unique set of authors (in this history segment)
    users = set(strip_email(c.author) for c in raw_history)
    history = []
    for c in raw_history:
        split = c.author.index('<')
        name = c.author[:split]
        email = c.author[(split + 1):-1]
        time = relative_time(c.commit_time)
        message, obj = interpret(c.message, tracker)

        snippet = title = link = button = None

        if type(obj) is Comment:
            snippet = cut(obj.content, 190)
            link = url_for('issues.view', id=obj.issue.id[:6]) + '#comment-' + obj.id[:6]
            button = obj.issue.id[:6]
        if type(obj) is Issue:
            title = obj.title
            snippet = cut(obj.content, 190)
            link = url_for('issues.view', id=obj.id[:6])
            button = obj.id[:6]

        history.append({'user': {'name': name, 'email': email},
                        'message': message,
                        'time': time,
                        'link': link,
                        'button': button,
                        'title': title,
                        'snippet': snippet
                        }
                       )

    return render_template('feed.html', history=history,
                           selected='feed', header=header, 
                           tracker=tracker, users=users)


def interpret(message, tracker):
    '''
    Look for an issue and/or comment id in the commit message
    and return the appropriate object.
    '''
    message = message[0].lower() + message[1:]
    last13 = message[-13:]
    print last13
    last6 = message[-6:]
    if looks_hashy(last13[:6]) and looks_hashy(last13[7:]):
        issue_id = last13[:6]
        comment_id = last13[7:]
        issue = Issue(tracker, issue_id)
        redacted = message[:-13]
        return redacted, Comment(issue, comment_id)
    elif looks_hashy(last6):
        try:
            redacted = message[:-6]
            return redacted, Issue(tracker, last6)
        except BadReference:
            pass
    return message, None
