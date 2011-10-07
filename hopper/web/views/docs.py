from flask import Blueprint, render_template

from hopper.web.utils import setup

docs = Blueprint('docs', __name__)

@docs.route('/')
@docs.route('/<name>')
def main(name=None):
    tracker, config = setup()
    header = 'Documentation for Hopper'
    docs = tracker.docs()
    if name:
        doc = tracker.doc(name + '.md')
    else:
        doc = docs[0]
    return render_template('docs.html', tracker=tracker, docs=docs,
                           doc=doc, selected='docs', header=header)
