try:
    import simplejson as json
except ImportError:
    import json
import hashlib
import glob
import os
import sys

def to_json(data):
    '''Abstracts the json.dumps method, providing error handling.'''
    return json.dumps(data, sort_keys=True, indent=4)

def from_json(data):
    '''Abstracts the json.loads method, providing error handling.'''
    return json.loads(data)

def get_hash(text):
    '''SHA1 the text and return the hexdigest.'''
    return hashlib.sha1(text).hexdigest()

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
