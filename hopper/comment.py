import time
import os
import glob

from hopper.files import BaseFile, JSONFile
from hopper.utils import to_json, get_hash
from hopper.errors import BadReference, AmbiguousReference

class Comment(JSONFile):
    """Represents an issue's comment."""
    
    def __init__(self, issue, id=None, **kwargs):
        self.fields = {
              'author'   : {
                  'name'  : None,
                  'email' : None,
                  'avatar': None
                  },
              'content'   : None,
              'timestamp' : None,
              'id'        : None,
              'event'     : False,
              'event_data': None,
              }
        self.issue = issue
        if id is not None:
            self.id = self._resolve_id(id)
            self.from_file(issue.get_comment_path(self.id))
        super(BaseFile, self).__init__()

    def __eq__(self, other):
        return True if self.id == other.id else False

    def __ne__(self, other):
        return True if self.id != other.id else False

    def __repr__(self):
        return '<Comment %s>' % self.id[:6]

    def save(self):
        """Save the comment to file."""
        self.timestamp = time.time()
        self.id = get_hash(to_json(self.fields))
        if not os.path.isdir(self.issue.paths['comments']):
            os.mkdir(self.issue.paths['comments'])
        # replace the issue in the db
        self.issue.tracker.db.insert(self.issue)
        return self.to_file(self.issue.get_comment_path(self.id))

    def delete(self):
        """Delete the comment's disk representation."""
        os.remove(self.issue.get_comment_path(self.id))

    def _resolve_id(self, id):
        """Resolve partial ids and verify the comment exists."""
        if len(id) == 40:
            if os.path.exists(self.issue.get_comment_path(id)):
                return id
            else:
                raise BadReference('No matching comment on disk: %s' % id)
        # glob the path returned by the issue helper method
        matches = glob.glob(self.issue.get_comment_path(id + '*'))
        # no matches, raise bad ref:
        if not matches:
            raise BadReference('No matching comment on disk: %s' % id)
        # multiple matches, raise ambiguous ref:
        if len(matches) > 1:
            raise AmbiguousReference('Multiple comments matched that id fragment')
        # one match, return the match
        match_id = os.path.basename(matches[0])
        print match_id
        return match_id
