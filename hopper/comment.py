import time

from item import Item

class Comment(Item):
    def __init__(self, issue):
        self.fields = {
              'author': {
                  'name': None,
                  'email': None
                  },
              'content': None,
              'timestamp': None
              }
        self.issue = issue
    
    def add(self, save_issue=False):
        '''
        Append the comment to the issue and call the issue's save
        method.

        :param save_issue: save the associated issue. 
        '''
        self.timestamp = time.time()
        self.issue.fields['comments'].append(self.fields)
        if save_issue:
            self.issue.save()
