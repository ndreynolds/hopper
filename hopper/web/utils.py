"""
  hopper.web.utils
  ================
  Utility functions for web views.
"""

from flask import flash, request, current_app
import string
import re

from hopper.tracker import Tracker
from hopper.config import UserConfig

# Handles json/simplejson import
from hopper.utils import to_json as json

def setup():
    """
    Return the tracker and config. 
    
    It also sets the flash to an environment warning to let the user know
    they are running the tracker locally and as <name>. We only do this
    the first time setup() is called per web server process.
    """
    config = UserConfig()
    # Use current_app so we don't have circular imports.
    tracker = Tracker(current_app.GLOBALS['tracker'])
    if current_app.GLOBALS['first_request']:
        flash('Running Hopper locally as %s' % config.user['name'])
        current_app.GLOBALS['first_request'] = False
        # Make sure the SQLite db is in sync with the JSON db.
        tracker.db._replicate()
    return tracker, config


def to_json(data):
    """
    Same as Flask's jsonify, but allows top-level arrays. 

    :param data: a python dictionary or list.
    """
    json_response = json(data, indent=None if request.is_xhr else 2)
    return current_app.response_class(json_response, mimetype='application/json')


def looks_hashy(text):
    """
    Return True if the string could be (part of) a 40 byte SHA1 hex 
    digest. Intended for auto-generating links to issues.

    :param text: a string
    """
    return all(ch in string.hexdigits for ch in text) and len(text) < 40


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
        pages = [p for p in range(1, page + 6) if p in 
                 range(1, num_pages + 1)]
    else:
        pages = [p for p in range(page - 3, page + 4) if p in 
                 range(1, num_pages + 1)]
    if not num_pages - 1 in pages:
        pages += [False, num_pages - 1, num_pages]
    if not 2 in pages: 
        pages = [1, 2, False] + pages
    return pages


def highlight(text, keyword, condense=True):
    """
    Surround instances of keyword in text with the surround tuple.
    Just replaces all instances with the entire concatenated string.

    :param text: string of text to perform highlights within.
    :param keyword: string to highlight.
    :param condense: if True, condense the highlighted text to a reasonable
                     size. A maximum of 500 characters will be displayed, 
                     starting with the first match and ending 500 characters 
                     afterward.
    """

    # We're passing this func to re.sub to highlight each match
    # Can't just sub the keyword b/c we need to retain case.
    def hilite(m):
        return "<span class='highlighted'>%s</span>" % m.group()

    # Compile the pattern--it's case-insensitive
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)

    # Substitute the pattern with the return value of hilite for each match in
    # text:
    subd = re.sub(pattern, hilite, text)

    # Condense to (first_match or 0) to (last_match or end)
    if condense:
        try:
            start = subd.index("<span class='highlighted'>") - 30
            end = subd.rindex("<span class='highlighted'>") + len(keyword) + 37 
            if start < 0:
                start = 0
            if end - start > 500:
                end = start + 500
            return subd[start:end]
        except ValueError:
            return subd[:200]
    return subd
