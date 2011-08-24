import time

from item import Item

class Comment(Item):
    def __init__(self, issue):
        self.fields = {
              u'author': {
                  'name': None,
                  'email': None
                  },
              u'content': None,
              u'timestamp': None
              }
        self.issue = issue
    
    def add(self):
        '''
        Append the comment to the issue and call the issue's save
        method.
        '''
        self.timestamp = time.time()
        self.issue.fields['comments'].append(self.fields)
