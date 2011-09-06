import time
import hashlib

from hopper.item import Item
from hopper.utils import to_json, get_hash

class Comment(Item):
    '''
    Represents an issue's comment. The Comment class does not directly
    write its objects to file, this is done through the Issue.save() method.
    '''
    
    def __init__(self, issue, id=None, **kwargs):
        self.fields = {
              'author': {
                  'name': None,
                  'email': None
                  },
              'content': None,
              'timestamp': None,
              'id': None
              }
        # If an id was given, find the matching comment and merge its items
        # with the defaults.
        self.issue = issue
        if id is not None:
            self.read(id)
        self._set_fields()

    def read(self, id):
        '''Read in a comment from the issue.'''
        matches = filter(lambda x: x.id == id, self.issue.comments)
        if len(matches): 
            comment = matches[0]
            self.fields = dict(self.fields.items() + comment.fields.items())

    def save(self, save_issue=False):
        '''
        Append the comment to the issue and optionally call the issue's save
        method.

        :param save_issue: save the associated issue. 
        '''
        self.timestamp = time.time()
        self.id = get_hash(to_json(self.fields))
        # delete the existing comment, if it exists.
        self.delete()
        self.issue.comments.append(self)
        if save_issue:
            self.issue.save()

    def delete(self, save_issue=False):
        '''
        Delete the instantiated comment from the issue, if it's even
        there.
        '''
        for comment in self.issue.comments:
            if comment.id == self.id:
                self.issue.comments.remove(comment)

    @classmethod
    def rm(cls, issue, id, save_issue=False):
        '''
        Class method to remove the specified comment from the
        issue without needing to instantiate it. Use delete() to
        delete the instantiated comment.
        '''
        for comment in issue.comments:
            if comment.id == id:
                issue.comments.remove(comment)
