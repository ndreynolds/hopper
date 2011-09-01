from hopper.tracker import Tracker
from hopper.issue import Issue
from hopper.comment import Comment
from hopper.utils import get_uuid

import os
import shutil

class TestEnv(object):
    '''
    An environment for testing Hopper.
    
    Methods to make a tracker.
    '''
    def __init__(self):
        self.tracker = self.make_tracker()

    def make_tracker(self, direc=None, name=None):
        '''
        Make a tracker in the current directory with the given or a
        randomly generated name. This is called automatically on init.
        It is left public for scenarios where having multiple trackers
        is desired.
        '''
        if name is not None:
            path = name
        else:
            path = get_uuid()
        if direc is not None:
            path = os.path.join(direc, path)
        return Tracker.new(path)

    def rm_tracker(self, path=None):
        '''
        Remove the environment's tracker, or delete the tracker at the
        given path. Be careful with this one, as it will try to delete 
        any path you give it, tracker or not.
        '''
        if path is None:
            path = self.tracker.paths['root']
        shutil.rmtree(path)

    def make_issue(self, fields=None):
        '''Make an issue'''
        issue = Issue()
        if fields is not None:
            issue.fields = dict(issue.fields.items() + fields.items())
        return issue
