from flask import Blueprint, render_template, request

from hopper.web.utils import setup

settings = Blueprint('settings', __name__)

@settings.route('/', methods=['GET', 'POST'])
def main():
    tracker, config = setup()
    if request.method == 'POST':
        tracker.config.name = request.form['name']
        tracker.config.save()
    header = 'Settings for %s' % tracker.config.name
    return render_template('settings.html', tracker=tracker, 
                           name=tracker.config.name, selected='settings', 
                           header=header)
