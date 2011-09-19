'''
Utility functions for the Hopper Flask app.
'''

from flask import flash, request, current_app

from hopper.tracker import Tracker
from hopper.config import Config

# Handles json/simplejson import
from hopper.utils import to_json as json

def setup():
    '''
    Return the tracker and config. 
    
    It also sets the flash to an environment warning to let the user know
    they are running the tracker locally and as <name>. We only do this
    the first time setup() is called per web server lifetime.
    '''
    config = Config()
    # Use current_app so we don't have circular imports.
    if current_app.GLOBALS['first_request']:
        flash('Running Hopper locally as %s' % config.user['name'])
        current_app.GLOBALS['first_request'] = False
    return Tracker(current_app.GLOBALS['tracker']), config

def to_json(data):
    '''
    Same as Flask's jsonify, but allows top-level arrays. There are cited
    security reasons for not doing this, but it makes for an annoying API. 
    '''
    json_response = json(data, indent=None if request.is_xhr else 2)
    return current_app.response_class(json_response, mimetype='application/json')
