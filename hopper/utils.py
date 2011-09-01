try:
    import simplejson as json
except ImportError:
    import json
import hashlib
import glob
import os
import sys
import time
import random

def to_json(data):
    '''
    Returns sorted & indented JSON from the best json module available.

    By defining json helpers here, we don't have to play the try-except 
    import game in every file.
    '''
    return json.dumps(data, indent=4)

def from_json(data):
    '''Returns python objects loaded from a JSON string.'''
    return json.loads(data)

def get_hash(text):
    '''SHA1 the text and return the hexdigest.'''
    return hashlib.sha1(text).hexdigest()

def get_uuid(salt=None):
    '''Return a UUID generated from the UTC ts and a random float.'''
    if salt is None:
        # user can provide a salt to use instead of the random float. 
        salt = str(random.random())
    # probably overkill to use both random and time
    return get_hash(str(time.time()) + salt)

def match_path(path, get_all=False):
    '''
    Match a path using glob. Return scenarios:
        No matches => None
        One or more matches => first matching path as string 
        No matches and get_all => []
        Matches and get_all => [path1, path2, path3]
    '''
    if path.startswith('~'):
        path = os.path.join(os.getenv('HOME'), path[1:])
    matches = glob.glob(path)
    if get_all:
        return matches
    if matches:
        return glob.glob(path)[0]
    else:
        return None
