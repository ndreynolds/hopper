from __future__ import with_statement
import time
import os

from config import Config
from item import Item
from utils import to_json, from_json, get_hash

class Issue(Item):
    '''
    Defines an issue (or bug, if you prefer that term). Issues are
    stored as dictionaries.  The class handles the conversion to JSON.

    :param tracker: a hopper.Tracker object that stores information
                    about and the location of the tracker in question.
    :param identifier: an issue identifier. If this is provided, the 
                       existing issue will be read from the tracker, 
                       rather than creating a new one.
    '''

    def __init__(self, tracker, id=None):
        self.fields = {
                'title': None,
                'status': 'open',
                'labels': [],
                'content': None,
                'created': None,
                'updated': None
                'comments': [],
                }
        self.tracker = tracker
        self._set_fields()
        if id is not None:
            self.id = id
            self.read(id)
    
    def read(self, id):
        '''
        Read the issue with the given identifier.

        This is used internally, but could also be used to read in
        another issue without creating a new object.
        '''
        path = self.tracker.get_issue_path(id)
        with open(path, 'r') as fp:
            issue_json = fp.read()
        self.fields = from_json(issue_json)

    def save(self):
        '''Save the issue to file using JSON.'''
        if not hasattr(self, 'id'):
            # IDs are generated from the JSON dump of the
            # issue. This includes the UTC-format timestamp, so 
            # they can be considered effectively unique.
            self.created = time.time()
            self.id = get_hash(to_json(self.fields))
        
        # We need to set updated, even if it's the same as created,
        # so we have a consistent timestamp to sort issues by.
        self.updated = time.time()
        json_dump = to_json(self.fields)
        path = self.tracker.get_issue_path(self.id, False)
        with open(path, 'w') as fp:
            fp.write(json_dump)
