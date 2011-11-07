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
from docutils import core
from docutils.writers.html4css1 import Writer, HTMLTranslator

def to_json(data, indent=4):
    """
    Returns sorted & indented JSON from the best json module available.

    :param data: a python structure that can be converted to JSON (i.e.
                 a list or dictionary).
    """
    # Main purpose here is to avoid doing the json module conditional
    # logic in every script that uses it.
    return json.dumps(data, indent)


def from_json(data):
    """
    Returns python objects loaded from a JSON string.

    :param data: a valid JSON-encoded string.
    """
    return json.loads(data)


def get_hash(text):
    """
    SHA1 the text and return the hexdigest.
    """
    return hashlib.sha1(text).hexdigest()


def get_uuid(salt=None):
    """
    Return a UUID generated from the UTC ts and a random float.

    :param salt: if given, this will be used instead of the call to
                 ``random.random()``.
    """
    if salt is None:
        # user can provide a salt to use instead of the random float. 
        salt = str(random.random())
    # probably overkill to use both random and time
    return get_hash(str(time.time()) + salt)


def relative_time(ts):
    """
    Return a human-parseable time format from a UTC timestamp.

    :param ts: a timestamp, given as a float (or something that can
               be converted to one).
    """
    if type(ts) is not float:
        try:
            ts = float(ts)
        except TypeError:
            return 'invalid time'

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
    """Convert markdown to html."""
    return markdown(text, ['codehilite'])


class NoHeaderHTMLTranslator(HTMLTranslator):
    """
    Adapted from: 
        http://code.activestate.com/recipes/193890-using-rest-
            restructuredtext-to-create-html-snippet/
    """
    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.head_prefix = ['', '', '', '', '']
        self.body_prefix = []
        self.body_suffix = []
        self.stylesheet  = []


def rst_to_html(text):
    """Convert reStructured text to html."""
    w = Writer()
    w.translator_class = NoHeaderHTMLTranslator
    return core.publish_string(text, writer=w)


def match_path(path, get_all=False):
    """
    Match a path using glob. 

    :param path: the path to match.
    :param get_all: if True, return the list of matches, by default it
                    will return the first match.
    
    Return scenarios:
        No matches             => None
        One or more matches    => first matching path as string 
        No matches and get_all => []
        Matches and get_all    => [path1, path2, path3]
    """
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
    """
    Apply the function, f, to attribute, attr, of each object in obj_list

    This was implemented for things like humanizing issues' timestamps before
    sending them out to the template.

    :param obj_list: a list of objects.
    :param attr: an attribute that each object in **obj_list** should have.
    :param f: a function to apply to each each object's **attr**.
    """ 
    for obj in obj_list:
        val = getattr(obj, attr)
        val = f(val)
        setattr(obj, attr, val)
    return obj_list # Lists are mutable so using this isn't necessary.


def cut(text, length, add_elipses=True):
    """
    Cut text off after the given length, optionally adding elipses to 
    the end.

    :param text: string to cut
    :param length: slice off chars after this int.
    :param add_elipses: if True, append ``...`` to the end, if the 
                        number of chars in text exceeded length.
    """
    if len(text) <= length:
        return text
    elif add_elipses:
        return text[:length] + '...'
    return text[:length]


def wrap(text, width=80):
    """
    Intelligently wrap text to a set width.

    :param text: text to wrap.
    :param width: number of columns to wrap to.
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                    word),
                   text.split(' ')
                  )


def strip_email(author):
    """
    Strips the email address (i.e. <%s>) from the Git commit author
    string, or any similar one.

    :param author: string, formatted like 'Nick Reynolds <ndreynolds@gmail.com'
    """
    if '<' in author or '@' in author:
        first_bracket = author.index('<')
        # return the string before the first angle bracket
        return author[:first_bracket - 1]
    # didn't contain the email address, return untouched.
    return author
