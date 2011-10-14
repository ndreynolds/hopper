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
    '''
    '''
    tracker, config = setup()

    # get the url params
    sort = request.args.get('sort')
    order = request.args.get('order')
    try:
        page = int(request.args.get('page'))
    except TypeError:
        page = 1
    except ValueError:
        page = 1

    reverse = True 
    sort_by = 'updated'
    issues_per_page = 15 

    if order == 'asc':
        reverse = False
    if sort in ['id', 'title', 'updated']:
        sort_by = sort
    if page > 1: 
        # If we're on page 3, the offset should be 50.
        offset = (page - 1) * issues_per_page
        issues_, n = tracker.issues(n=issues_per_page, offset=offset, 
                                    sort_by=sort_by, reverse=reverse, 
                                    return_num=True, conditions={'status': status})
    else:
        issues_, n = tracker.issues(n=issues_per_page, sort_by=sort_by, 
                                    reverse=reverse, return_num=True, 
                                    conditions={'status': status})

    # get the number of pages
    num_pages = n / issues_per_page

    # get pages to link to
    if num_pages > 1:
        pages = pager(page, num_pages)
    else:
        pages = None

    # set the context header
    context = 'open' if status == 'open' else 'closed'
    header = 'Viewing %s issues for %s' % (context, tracker.config.name)

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
                               selected='issues', status=status, 
                               sorted_by=sort_by, page=page, pages=pages,
                               num_pages=num_pages, order=order,
                               header=header, n=n, tracker=tracker)


@issues.route('/search/<query>')
def search(query):
    header = "Search results for '%s'" % query
    pass


@issues.route('/new', methods=['GET', 'POST'])
def new():
    tracker, config = setup()
    header = 'Create a new issue'
    if request.method == 'POST':
        issue = Issue(tracker)
        issue.content = request.form['content']
        issue.title = request.form['title']
        labels = request.form['labels']
        if labels:
            issue.labels = labels.split(',')
        else:
            issue.labels = []
        issue.author['name'] = config.user['name']
        issue.author['email'] = config.user['email']
        if issue.save():
            tracker.autocommit(message='Created a new issue %s' % issue.id[:6], 
                               author=config.user)
            return redirect(url_for('issues.view', id=issue.id)) 
        else:
            flash('There was an error saving your issue.')
            return render_template('new.html', selected='issues', 
                                   header=header, tracker=tracker)
    else:
        return render_template('new.html', selected='issues', 
                               header=header, tracker=tracker)


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
        if issue.save(): # ping the issue (updated = now)
            tracker.autocommit(message='Commented on issue %s/%s' % \
                                        (issue.id[:6], comment.id[:6]),
                               author=config.user)
        else:
            flash('There was an error saving your comment.')
        return redirect(url_for('issues.view', id=issue.id))
    else:
        issue.updated = relative_time(issue.updated)
        issue.created = relative_time(issue.created)
        issue.content = markdown_to_html(issue.content)
        comments = issue.comments()
        header = 'Viewing Issue &nbsp;<span class="fancy-monospace">%s</span>' % issue.id[:6]
        if comments:
            map_attr(comments, 'timestamp', relative_time)
            map_attr(comments, 'content', markdown_to_html)
        return render_template('issue.html', issue=issue,
                               comments=comments, selected='issues',
                               config=config, header=header, tracker=tracker)


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
        return redirect(url_for('issues.view', id=issue.id))


@issues.route('/action/open/<id>')
def open(id):
    tracker, config = setup()
    issue = tracker.issue(id)
    if issue:
        issue.status = 'open'
        if not issue.save():
            flash('Could not reopen the issue')
        return redirect(url_for('issues.view', id=issue.id))


def fetch_issues():
    pass


def pager(page, num_pages):
    '''
    Generates a list of pages to link to based on the current page
    and the total number of pages.

    For example, if page=1 and there are at least 8 pages, it will 
    return [1,2,3,4,5,6,7,8].
    '''
    if page == 1:
        pages = [p for p in range(1, page + 6) if p in range(1, num_pages + 1)]
    else:
        pages = [p for p in range(page - 3, page + 4) if p in range(1, num_pages + 1)]
    if not num_pages - 1 in pages:
        pages += [False, num_pages - 1, num_pages]
    if not 2 in pages: 
        pages = [1, 2, False] + pages
    print pages
    return pages
