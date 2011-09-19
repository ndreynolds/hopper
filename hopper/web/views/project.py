from flask import Blueprint, render_template

from hopper.web.utils import setup
from hopper.utils import markdown_to_html

project = Blueprint('project', __name__)

@project.route('/')
def home():
    tracker, config = setup()
    readme = markdown_to_html(tracker.read('README.md'))
    source = markdown_to_html(tracker.read('SOURCE.md'))
    return render_template('project.html', readme=readme,
            source=source, selected='project')
