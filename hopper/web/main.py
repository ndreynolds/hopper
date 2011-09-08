from flask import Flask, render_template, url_for, request, redirect, \
                  flash
from hopper.tracker import Tracker
from hopper.issue import Issue
from hopper.comment import Comment
from hopper.filter import Filter
from hopper.config import Config
from hopper.utils import relative_time, markdown_to_html, map_attr

import json

app = Flask(__name__)
app.secret_key = 'sdgasd6t4ry43y45SADGVQ43Y345RQw356y45sDGDSgSDG'
TRACKER = None
DEBUG = True
FIRST_REQUEST = True

links = ['feed', 'issues', 'settings']

def start(path, port=5000, debug=DEBUG, external=False):
    '''
    Run the Hopper tracker at the given path. Allows for setting the port,
    debug mode, and whether or not it's externally visible. 

    Running it on port 80 is possible but will usually require being root.
    '''
    global TRACKER
    TRACKER = path

    # Try and get an int out of the port param, set to 5000 if anything
    # goes wrong.
    if type(port) in [int, str]:
        try:
            port = int(port)
        except ValueError:
            port = 5000
    else:
        port = 5000

    if external:
        # Run the app on a public IP. Debug will be off.
        app.debug=False
        app.run(host='0.0.0.0', port=port)
    else:
        # Run the app on the localhost, using the DEBUG const.
        app.debug = debug
        app.run(port=port)

def to_json(data):
    '''
    Same as Flask's jsonify, but allows top-level arrays. There are security
    reasons for not doing this, but I'm choosing to ignore them for now. 
    '''
    json_response = json.dumps(data, indent=None if request.is_xhr else 2)
    return app.response_class(json_response, mimetype='application/json')

def get_tracker():
    global FIRST_REQUEST
    if FIRST_REQUEST:
        config = Config()
        flash('Running Hopper locally as %s' % config.user['name'])
        FIRST_REQUEST = False
    return Tracker(TRACKER_ROOT)

@app.route('/')
def feed():
    tracker = get_tracker()
    return to_json([i.fields for i in tracker.issues()])

@app.route('/issues/<status>')
@app.route('/issues/', methods=['GET', 'POST'])
def issues(status='open'):
    tracker = get_tracker()
    sort = request.args.get('sort')
    order = request.args.get('order')
    reverse = True 
    sort_by = 'updated'
    if order == 'asc':
        reverse = False
    if sort in ['id', 'title', 'updated']:
        sort_by = sort
    if status == 'closed':
        issues = tracker.issues(n=20, sort_by=sort_by, \
                reverse=reverse, conditions={'status': 'closed'})
    else:
        issues = tracker.issues(n=20, sort_by=sort_by, \
                reverse=reverse, conditions={'status': 'open'})

    map_attr(issues, 'updated', relative_time)
    map_attr(issues, 'created', relative_time)
    if request.json is not None:
        return to_json(request.json)
    else:
        return render_template('issues.html', issues=issues, links=links, 
                selected='issues', status=status, sorted_by=sort_by, order=order)

@app.route('/issues/new', methods=['GET', 'POST'])
def new():
    tracker = get_tracker()
    if request.method == 'POST':
        config = Config()
        issue = Issue(tracker)
        issue.content = request.form['content']
        issue.title = request.form['title']
        issue.labels = request.form['labels']
        issue.author['name'] = config.user['name']
        issue.author['email'] = config.user['email']
        if issue.save():
            return redirect(url_for('issue', id=issue.id)) 
        else:
            flash('There was an error saving your issue')
            return render_template('new.html')
    else:
        return render_template('new.html')

@app.route('/issues/view/<id>', methods=['GET', 'POST'])
def issue(id):
    '''
    Renders the issues template. Alternatively, it will respond with 
    JSON when the request mimetype is 'json/application'. The JSON
    requests can contain filter objects. Filters are part of the UI
    and we must re-request the issues each time a filter changes.
    '''
    tracker = get_tracker()
    issue = tracker.issue(id)
    if request.method == 'POST':
        config = Config()
        comment = Comment(issue)
        comment.content = request.form['content']
        comment.author['name'] = config.user['name']
        comment.author['email'] = config.user['email']
        comment.save()
        return redirect(url_for('issue', id=issue.id))
    else:
        issue.updated = relative_time(issue.updated)
        issue.created = relative_time(issue.created)
        issue.content = markdown_to_html(issue.content)
        comments = issue.comments()
        if comments:
            map_attr(comments, 'timestamp', relative_time)
            map_attr(comments, 'content', markdown_to_html)
        return render_template('/issue.html', issue=issue, \
                comments=comments, links=links, selected='issues')

@app.route('/settings')
def settings():
    tracker = get_tracker()
    return render_template('/settings.html')

@app.route('/issues/close/<id>')
def close(id):
    tracker = get_tracker()
    issue = tracker.issue(id)
    if issue:
        issue.status = 'closed'
        if not issue.save():
            flash('Could not close the issue')
        return redirect(url_for('issue', id=issue.id))

@app.route('/issues/open/<id>')
def open(id):
    tracker = get_tracker()
    issue = tracker.issue(id)
    if issue:
        issue.status = 'open'
        if not issue.save():
            flash('Could not reopen the issue')
        return redirect(url_for('issue', id=issue.id))

if __name__ == '__main__':
    app.debug = DEBUG
    TRACKER_ROOT = '/home/ndreynolds/repos/hopper2/hopper/new_tracker'
    app.run()
