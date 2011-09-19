'''
Views for issues:
    index, view, new, action/ACTION
'''

from flask import Blueprint, request, redirect, url_for, render_template, \
                  flash

from hopper.issue import Issue
from hopper.comment import Comment
from hopper.utils import relative_time, markdown_to_html, map_attr

from hopper.web.utils import setup, to_json

issues = Blueprint('issues', __name__)

@issues.route('/<status>')
@issues.route('/', methods=['GET', 'POST'])
def index(status='open'):
    tracker, config = setup()

    # get the url params
    sort = request.args.get('sort')
    order = request.args.get('order')
    page = request.args.get('page') if True else 1

    reverse = True 
    sort_by = 'updated'
    if order == 'asc':
        reverse = False
    if sort in ['id', 'title', 'updated']:
        sort_by = sort
    if status == 'closed':
        issues_ = tracker.issues(n=20, sort_by=sort_by, \
                reverse=reverse, conditions={'status': 'closed'})
    else:
        issues_ = tracker.issues(n=20, sort_by=sort_by, \
                reverse=reverse, conditions={'status': 'open'})

    # humanize the timestamps
    map_attr(issues_, 'updated', relative_time)
    map_attr(issues_, 'created', relative_time)

    # Currently, some labels are CSV-formatted while the others are
    # JSON arrays. To support the prototypes that used CSV we have
    # to do the conversion. This should be taken out before 1.0.
    for issue in issues_:
        if type(issue.labels) is str or type(issue.labels) is unicode:
            # Filter anything that doesn't return True (i.e. '')
            issue.labels = filter(lambda x: x, issue.labels.split(','))

    if request.json is not None:
        return to_json(request.json)
    else:
        return render_template('issues.html', issues_=issues_, 
                selected='issues', status=status, sorted_by=sort_by, 
                page=page, order=order)

@issues.route('/new', methods=['GET', 'POST'])
def new():
    tracker, config = setup()
    if request.method == 'POST':
        issue = Issue(tracker)
        issue.content = request.form['content']
        issue.title = request.form['title']
        issue.labels = request.form['labels'].split(',')
        issue.author['name'] = config.user['name']
        issue.author['email'] = config.user['email']
        if issue.save():
            return redirect(url_for('issue', id=issue.id)) 
        else:
            flash('There was an error saving your issue')
            return render_template('new.html')
    else:
        return render_template('new.html', selected='issues')

@issues.route('/view/<id>', methods=['GET', 'POST'])
def view(id):
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
                comments=comments, selected='issues',
                config=config)

@issues.route('/settings')
def settings():
    tracker, config = setup()
    return render_template('/settings.html')

@issues.route('/action/close/<id>')
def close(id):
    tracker, config = setup()
    issue = tracker.issue(id)
    if issue:
        issue.status = 'closed'
        if not issue.save():
            flash('Could not close the issue')
        return redirect(url_for('issue', id=issue.id))

@issues.route('/action/open/<id>')
def open(id):
    tracker, config = setup()
    issue = tracker.issue(id)
    if issue:
        issue.status = 'open'
        if not issue.save():
            flash('Could not reopen the issue')
        return redirect(url_for('issue', id=issue.id))
