from flask import Blueprint, render_template

from hopper.web.utils import setup

settings = Blueprint('settings', __name__)

@settings.route('/')
def main():
    tracker, config = setup()
    header = 'Settings for %s' % tracker.config.name
    return render_template('settings.html', tracker=tracker, 
                           selected='settings', header=header)
