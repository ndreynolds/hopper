from flask import Blueprint, render_template

from hopper.web.utils import setup, looks_hashy
from hopper.utils import relative_time
from hopper.errors import BadReference

feed = Blueprint('feed', __name__)

@feed.route('/')
def main():
    tracker, config = setup()
    header = 'Recent Activity for %s' % tracker.config.name
    raw_history = tracker.history(20)
    history = []
    for c in raw_history:
        split = c.author.index('<')
        name = c.author[:split]
        email = c.author[(split + 1):-1]
        time = relative_time(c.commit_time)
        message = c.message[:-6]
        # We're trying to parse issue ids from the commit message.
        maybe_link = c.message[-6:] 
        # Looks like hex digest (no more than 40 chars, hexadecimal)?
        link = maybe_link if looks_hashy(maybe_link) else None
        # Try and find the issue with that link. 
        try:
            i = tracker.issue(link)
        except BadReference:
            link = None
        if link is None:
            message = c.message
            changes = None
        else:
            if len(i.content) > 190:
                changes = i.content[:190] + '...'
            else:
                changes = i.content
        message = message[0].lower() + message[1:]
        history.append({'user': {'name': name, 'email': email},
                        'message': message,
                        'time': time,
                        'link': link,
                        'changes': changes
                        }
                       )

    return render_template('feed.html', history=history,
                           selected='feed', header=header, 
                           tracker=tracker)
