from flask import flash, request, current_app
import string

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
