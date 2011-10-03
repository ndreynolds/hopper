try:
    import simplejson as json
except ImportError:
    import json
import hashlib
import glob
import os
import time
import random
from datetime import datetime
from markdown import markdown

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


def relative_time(ts):
    '''Return a human-parseable time format from a UTC timestamp.'''
    ts = datetime.fromtimestamp(ts)
    delta = datetime.now() - ts
    days = delta.days
    hours = delta.seconds / 3600
    minutes = delta.seconds % 3600 / 60
    
    if days > 0:
        if days == 1:
            return '1 day ago'
        return '%d days ago' % days
    if hours > 0:
        if hours == 1:
            return '1 hour ago'
        return '%d hours ago' % hours
    if minutes > 0:
        if minutes == 1:
            return '1 minute ago'
        return '%d minutes ago' % minutes
    return 'just now'


def markdown_to_html(text):
    return markdown(text, ['codehilite'])


def match_path(path, get_all=False):
    '''
    Match a path using glob. 

    :param path: the path to match.
    :param get_all: if True, return the list of matches, by default it
                    will return the first match.
    
    Return scenarios:
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
        return matches[0]
    else:
        return None


def map_attr(obj_list, attr, f):
    '''
    Apply the function, f, to attribute, attr, of each object in obj_list

    This was implemented for things like humanizing issues' timestamps before
    sending them out to the template.

    :param obj_list: a list of objects.
    :param attr: an attribute that each object in **obj_list** should have.
    :param f: a function to apply to each each object's **attr**.
    ''' 
    for obj in obj_list:
        val = getattr(obj, attr)
        val = f(val)
        setattr(obj, attr, val)
    return obj_list # Lists are mutable so using this isn't necessary.


def cut(text, length, add_elipses=True):
    '''
    Cut text off after the given length.
    '''
    if len(text) <= length:
        return text
    elif add_elipses:
        return text[:length] + '...'
    return text[:length]

def wrap(text, width=80):
    '''
    Intelligently wrap text to a set width.

    :param text: text to wrap.
    :param width: number of columns to wrap to.
    '''

    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                    word),
                   text.split(' ')
                  )
