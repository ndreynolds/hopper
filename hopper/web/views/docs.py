from flask import Blueprint, render_template, abort

from hopper.web.utils import setup

docs = Blueprint('docs', __name__)

@docs.route('/')
@docs.route('/<name>')
def main(name=None):
    tracker, config = setup()
    header = 'Documentation for %s' % tracker.config.name
    docs = tracker.docs()
    if name:
        try:
            doc = tracker.doc(name)
            converted = doc.read(convert=True)
            markdown = doc.read()
        except OSError:
            abort(404)
    else:
        doc = docs[0]
        converted = doc.read(convert=True)
        markdown = doc.read()
    return render_template('docs.html', tracker=tracker, docs=docs,
                           doc=doc, markdown=markdown, converted=converted, 
                           selected='docs', header=header)
