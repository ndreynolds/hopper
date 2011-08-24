from __future__ import with_statement
import hashlib
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
                'comments': [],
                'created': None,
                'updated': None
                }
        self.new = True
        self.tracker = tracker
        self.set_fields()
        if id is not None:
            self.id = id
            self.read(id)
    
    def read(self, id):
        '''Read the issue with the given identifier.'''
        path = self.tracker.get_issue_path(id)
        with open(path, 'r') as fp:
            issue_json = fp.read()

        self.fields = from_json(issue_json)
        self.new = False

    def save(self):
        '''Save the issue.'''
        if self.new:
            self.fields['created'] = time.time()
        else:
            self.fields['updated'] = time.time()
        issue_json = to_json(self.fields)
        if self.new:
            # Identifier are generated from the JSON dump of the
            # issue. This includes the UTC-format timestamp, so 
            # the identifiers can be considered effectively unique.
            self.id = get_hash(issue_json)
        path = self.tracker.get_issue_path(self.id, False)
        with open(path, 'w') as fp:
            fp.write(issue_json)

        # The issue can no longer be new.
        self.new = False
