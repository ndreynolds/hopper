import time
import os

from hopper.files import BaseFile, JSONFile
from hopper.utils import to_json, get_hash

class Comment(JSONFile):
    '''Represents an issue's comment.'''
    
    def __init__(self, issue, id=None, **kwargs):
        self.fields = {
              'author': {
                  'name': None,
                  'email': None,
                  'avatar': None
                  },
              'content': None,
              'timestamp': None,
              'id': None
              }
        self.issue = issue
        if id is not None:
            self.from_file(issue.get_comment_path(id))
        super(BaseFile, self).__init__()

    def save(self):
        '''Save the comment to file.'''
        self.timestamp = time.time()
        self.id = get_hash(to_json(self.fields))
        if not os.path.isdir(self.issue.paths['comments']):
            os.mkdir(self.issue.paths['comments'])
        self.to_file(self.issue.get_comment_path(self.id))

    def delete(self):
        '''Delete the comment's disk representation.'''
        os.remove(self.issue.get_comment_path(self.id))
