from flask import flash
import json

from hopper.tracker import Tracker
from hopper.config import Config
from hopper.web.app import app, GLOBALS

def setup():
    '''
    Return the tracker and config. 
    
    It also sets the flash to an environment warning to let the user know
    they are running the tracker locally and as <name>. We only do this
    the first time setup() is called per web server lifetime.
    '''
    config = Config()
    global GLOBALS
    if GLOBALS['first_request']:
        flash('Running Hopper locally as %s' % config.user['name'])
        GLOBALS['first_request'] = False
    return Tracker(GLOBALS['tracker']), config

def to_json(data):
    '''
    Same as Flask's jsonify, but allows top-level arrays. There are security
    reasons for not doing this, but I'm choosing to ignore them for now. 
    '''
    json_response = json.dumps(data, indent=None if request.is_xhr else 2)
    return app.response_class(json_response, mimetype='application/json')
