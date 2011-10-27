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
    """
    Render the issue index view.

    :param status: 'open' or 'closed'
    """
    tracker, config = setup()

    # get the url params
    order = request.args.get('order', 'updated')
    direc = request.args.get('dir', 'asc')
    page = int(request.args.get('page', 1))

    # verify the params
    order = order if order in ['id', 'title', 'author'] else 'updated'
    reverse = True if direc == 'asc' else False
    per_page = 15 
    offset = (page - 1) * per_page if page > 1 else 0

    # run our query
    issues_ = tracker.query().select(limit=per_page, offset=offset, 
                                    status=status, order_by=order, 
                                    reverse=reverse)
    # humanize the timestamps
    map_attr(issues_, 'updated', relative_time)
    map_attr(issues_, 'created', relative_time)

    # get the number of issues by status
    n = tracker.query().count(status)

    # get the number of pages
    n_pages = n / per_page
    if n % per_page > 1:
        n_pages += 1

    # get pages to link to
    pages = pager(page, n_pages) if n > per_page else None

    # set the header
    header = 'Viewing %s issues for %s' % (status, tracker.config.name)

    if request.json is not None:
        return to_json(request.json)
    else:
        return render_template('issues.html', issues_=issues_, 
                               selected='issues', status=status, 
                               order=order, page=page, pages=pages,
                               num_pages=n_pages, asc=reverse,
                               header=header, n=n, tracker=tracker)


@issues.route('/search/<query>')
def search(query):
    header = "Search results for '%s'" % query
    pass


@issues.route('/new', methods=['GET', 'POST'])
def new():
    """Render the new issue view."""
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
    """
    Render the issue view to display information about a single issue.

    :param id: id of the issue to view.
    """
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
        header = 'Viewing Issue &nbsp;<span class="fancy-monospace">%s</span>' \
                % issue.id[:6]
        if comments:
            map_attr(comments, 'timestamp', relative_time)
            map_attr(comments, 'content', markdown_to_html)
        return render_template('issue.html', issue=issue,
                               comments=comments, selected='issues',
                               config=config, header=header, tracker=tracker)


@issues.route('/settings')
def settings():
    """Settings"""
    tracker, config = setup()
    return render_template('/settings.html')


@issues.route('/action/close/<id>')
def close(id):
    """
    Close an issue.

    :param id:
    """
    tracker, config = setup()
    issue = tracker.issue(id)
    if issue:
        issue.status = 'closed'
        if not issue.save():
            flash('Could not close the issue')
        return redirect(url_for('issues.view', id=issue.id))


@issues.route('/action/open/<id>')
def open(id):
    """
    Open an issue.

    :param id:
    """
    tracker, config = setup()
    issue = tracker.issue(id)
    if issue:
        issue.status = 'open'
        if not issue.save():
            flash('Could not reopen the issue')
        return redirect(url_for('issues.view', id=issue.id))


def pager(page, num_pages):
    """
    Generates a list of pages to link to based on the current page
    and the total number of pages.

    :param page: current page number
    :param num_pages: number of pages

    For example, if page=1 and there are at least 8 pages, it will 
    return [1,2,3,4,5,6,7,8].
    """
    print num_pages
    if page == 1:
        pages = [p for p in range(1, page + 6) if p in range(1, num_pages + 1)]
    else:
        pages = [p for p in range(page - 3, page + 4) if p in range(1, num_pages + 1)]
    if not num_pages - 1 in pages:
        pages += [False, num_pages - 1, num_pages]
    if not 2 in pages: 
        pages = [1, 2, False] + pages
    return pages
