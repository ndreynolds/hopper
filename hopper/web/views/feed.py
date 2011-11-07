from flask import Blueprint, render_template, url_for, request

from hopper.web.utils import setup, looks_hashy, to_json
from hopper.utils import relative_time, cut, strip_email
from hopper.errors import BadReference
from hopper.comment import Comment
from hopper.issue import Issue

feed = Blueprint('feed', __name__)

@feed.route('/')
def main():
    tracker, config = setup()

    # get the offset param (intended for javascript requests)
    offset = int(request.args.get('offset', 0))

    # Get up to 20 commits starting at whatever offset.
    raw_history = tracker.history(n=offset+20, offset=offset)

    # Don't want the performance hit of checking how many commits there are.
    # Instead, we're guessing that there's more if we get a full 20 in the 
    # first batch. 
    more_history = False if len(raw_history) < 20 else True

    # get the unique set of authors (in this history segment)
    users = set(strip_email(c.author) for c in raw_history)
    docs = tracker.docs()
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
                        'message': message.strip(),
                        'time': time,
                        'link': link,
                        'button': button,
                        'title': title,
                        'snippet': snippet
                        }
                       )
    # If the request is async, we're all set.
    if request.is_xhr:
        return to_json(history)

    # Otherwise, we have to get some more info.

    header = 'Recent Activity for %s' % tracker.config.name
    # Issue counts
    n_open = tracker.query().count('open')
    n_closed = tracker.query().count('closed')
    n_total = n_open + n_closed
    # Graph percentages
    # the subtraction is spacing for the CSS.
    g_open = (float(n_open) / n_total) * 100 - 2 if n_total > 0 else 0
    g_closed = (float(n_closed) / n_total) * 100 - 2 if n_total > 0 else 0
    g_open = 1 if g_open < 1 else g_open
    g_closed = 1 if g_closed < 1 else g_closed

    return render_template('feed.html', history=history,
                           selected='feed', header=header, 
                           tracker=tracker, users=users,
                           docs=docs, n_open=n_open, 
                           n_closed=n_closed, n_total=n_total,
                           g_open=g_open, g_closed=g_closed,
                           more_history=more_history)

@feed.route('/members')
def members():
    tracker, config = setup()
    header = "Everyone who's altered the %s time continuum." % tracker.config.name
    raw_history = tracker.history(all=True)
    # get the unique set of authors (in this history segment)
    users = set(strip_email(c.author) for c in raw_history)
    return render_template('members.html', header=header, 
                           tracker=tracker, users=users)

def interpret(message, tracker):
    """
    Look for an issue and/or comment id in the commit message
    and return the appropriate object.
    """
    message = message[0].lower() + message[1:]
    last13 = message[-13:]
    last6 = message[-6:]
    if looks_hashy(last13[:6]) and looks_hashy(last13[7:]):
        issue_id = last13[:6]
        comment_id = last13[7:]
        try:
            issue = Issue(tracker, issue_id)
            redacted = message[:-13]
            return redacted, Comment(issue, comment_id)
        except BadReference:
            pass
    elif looks_hashy(last6):
        try:
            issue = Issue(tracker, last6)
            redacted = message[:-6]
            return redacted, Issue(tracker, last6)
        except BadReference:
            pass
    return message, None
