from flask import Flask, render_template, url_for, request, redirect, \
                  flash
from hopper.tracker import Tracker
from hopper.issue import Issue
from hopper.comment import Comment
from hopper.config import Config
from hopper.utils import relative_time, markdown_to_html, map_attr

import json

app = Flask(__name__)
app.secret_key = 'sdgasd6t4ry43y45SADGVQ43Y345RQw356y45sDGDSgSDG'
VARS = {
        'tracker': None,
        'first_request': False,
        'debug': False
        }

links = ['feed', 'issues', 'settings']

def start(path, port=5000, debug=False, external=False):
    '''
    Run the Hopper tracker at the given path. Allows for setting the port,
    debug mode, and whether or not it's externally visible. 

    Running it on port 80 is possible but will usually require being root.
    '''
    # Try and get an int out of the port param, set to 5000 if anything
    # goes wrong.
    global VARS
    VARS['tracker'] = path
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
        # Run the app on the localhost.
        app.debug = debug
        app.run(port=port)

def to_json(data):
    '''
    Same as Flask's jsonify, but allows top-level arrays. There are security
    reasons for not doing this, but I'm choosing to ignore them for now. 
    '''
    json_response = json.dumps(data, indent=None if request.is_xhr else 2)
    return app.response_class(json_response, mimetype='application/json')

def setup():
    '''
    Return the tracker and config. 
    
    It also sets the flash to an environment warning to let the user know
    they are running the tracker locally and as <name>. We only do this
    the first time setup() is called per web server lifetime.
    '''
    config = Config()
    global VARS
    if VARS['first_request']:
        flash('Running Hopper locally as %s' % config.user['name'])
        VARS['first_request'] = False
    return Tracker(VARS['tracker']), config

@app.route('/')
def feed():
    tracker, config = setup()
    issues = tracker.issues()
    return render_template('issues.html', issues=issues, links=links, 
            selected='feed')

@app.route('/issues/<status>')
@app.route('/issues/', methods=['GET', 'POST'])
def issues(status='open'):
    tracker, config = setup()
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
    tracker, config = setup()
    if request.method == 'POST':
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
        return render_template('new.html', links=links, selected='issues')

@app.route('/issues/view/<id>', methods=['GET', 'POST'])
def issue(id):
    '''
    Renders the issues template. Alternatively, it will respond with 
    JSON when the request mimetype is 'json/application'. The JSON
    requests can contain filter objects. Filters are part of the UI
    and we must re-request the issues each time a filter changes.
    '''
    tracker, config = setup()
    issue = tracker.issue(id)
    if request.method == 'POST':
        comment = Comment(issue)
        comment.content = request.form['content']
        comment.author['name'] = config.user['name']
        comment.author['email'] = config.user['email']
        comment.save()
        issue.save() # ping the issue (updated = now)
        return redirect(url_for('issue', id=issue.id))
    else:
        issue.updated = relative_time(issue.updated)
        issue.created = relative_time(issue.created)
        issue.content = markdown_to_html(issue.content)
        comments = issue.comments()
        if comments:
            map_attr(comments, 'timestamp', relative_time)
            map_attr(comments, 'content', markdown_to_html)
        return render_template('/issue.html', issue=issue,
                comments=comments, links=links, selected='issues',
                config=config)

@app.route('/settings')
def settings():
    tracker, config = setup()
    return render_template('/settings.html')

@app.route('/issues/close/<id>')
def close(id):
    tracker, config = setup()
    issue = tracker.issue(id)
    if issue:
        issue.status = 'closed'
        if not issue.save():
            flash('Could not close the issue')
        return redirect(url_for('issue', id=issue.id))

@app.route('/issues/open/<id>')
def open(id):
    tracker, config = setup()
    issue = tracker.issue(id)
    if issue:
        issue.status = 'open'
        if not issue.save():
            flash('Could not reopen the issue')
        return redirect(url_for('issue', id=issue.id))

if __name__ == '__main__':
    app.debug = True
    VARS['tracker'] = '/home/ndreynolds/trackers/hopper'
    app.run()
