from flask import Blueprint, render_template

from hopper.web.utils import setup
from hopper.utils import relative_time, map_attr

feed = Blueprint('feed', __name__)

@feed.route('/')
def main():
    tracker, config = setup()
    header = 'Recent Activity for Hopper'
    history = tracker.history(20)
    map_attr(history, 'commit_time', relative_time)
    return render_template('feed.html', history=history,
                           selected='feed', header=header)
