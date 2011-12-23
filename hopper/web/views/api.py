"""Handles all the API calls. Each function returns JSON."""

from flask import Blueprint, request
from hopper.web.utils import setup, to_json
import hopper.web.views.issues as issue_view


api = Blueprint('api', __name__)


### /issues/*

@api.route('/issues/open')
def open_issues():
    """Returns open issues."""
    tracker, config = setup()
    issues = [i.fields for i in tracker.issues(status='open')]
    return to_json(issues)


@api.route('/issues/closed')
def closed_issues():
    """Returns closed issues."""
    tracker, config = setup()
    issues = [i.fields for i in tracker.issues(status='closed')]
    return to_json(issues)


@api.route('/issues/label/<label>')
@api.route('/issues/label/<label>/<status>')
def label(label, status=None):
    """
    Returns issues that have a given label.

    :param label: label to filter by.
    :param status: status to filter by, in addition to the label.
    """
    tracker, config = setup()
    issues = [i.fields for i in tracker.issues(label=label, status=status)]
    return to_json(issues)


@api.route('/issues/search/<query>')
@api.route('/issues/search/<query>/<status>')
def search(query, status=None):
    """
    Returns issues that match the search query.

    :param query: string to search issues for.
    :param status: status to filter by, in addition to the search query.
    """
    tracker, config = setup()
    issues = [i.fields for i in 
              tracker.query().search(sstr=query, status=status)]
    return to_json(issues)


@api.route('/issue/<id>')
def issue(id):
    """
    Return the issue with the given id.

    :param id: id of the issue. Only the number of characters necessary to
               uniquely identify it are required, but using more is a good
               idea.
    """
    tracker, config = setup()
    return to_json(tracker.issue(id).fields)


@api.route('/issue/<id>/close')
def close_issue(id):
    """
    Close the issue with the given id.

    :param id: id of the issue.
    """
    # this func and open_issue just hijack the issues view functions.
    # there's a lot to do here, and no sense repeating it.
    success = False
    if issue_view.close(id, redirect_after=False):
        success = True
    return to_json({'success': success})


@api.route('/issue/<id>/open')
def open_issue(id):
    """
    Open the issue with the given id.

    :param id: id of the issue.
    """
    success = False
    if issue_view.open(id, redirect_after=False):
        success = True
    return to_json({'success': success})


### /docs/* 

@api.route('/docs/<doc>')
def doc(doc):
    """
    Returns the given doc as html.

    :param doc: name of the doc.
    """
    tracker, config = setup()
    doc = tracker.doc(doc)
    return to_json({'content': doc.read(convert=True)})


@api.route('/docs/<doc>/raw')
def doc_raw(doc):
    """
    Returns the given doc in raw form.

    :param doc: name of the doc.
    """
    tracker, config = setup()
    doc = tracker.doc(doc)
    return to_json({'content': doc.read()})


@api.route('/docs/<doc>/edit', methods=['POST'])
def doc_edit(doc):
    """
    Given a POST request that contains an 'edited' field, the given
    doc's raw content is replaced.

    :param doc: name of the doc to edit.
    :returns: {'success': True} if there were no errors.
    """
    tracker, config = setup()
    success = False
    if request.form:
        doc = tracker.doc(doc)
        doc.write(request.form['edited'])
        success = True
    return to_json({'success': success})
