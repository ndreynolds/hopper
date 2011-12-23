from __future__ import with_statement
import time
import os
import shutil
import glob

from hopper.files import BaseFile, JSONFile
from hopper.comment import Comment
from hopper.utils import to_json, get_hash
from hopper.errors import BadReference, AmbiguousReference

class Issue(JSONFile):
    """
    Defines an issue (or bug, if you prefer that term). Issues are
    stored in flat files using JSON.  The parent class handles the 
    conversion to and from JSON.

    :param tracker: a Tracker object.
    :param id: an issue id (or SHA). If this is provided, the existing 
               issue will be read from the tracker. When omitted, a
               new issue is created.

    Before you can attach comments to an issue, the save method needs
    to get called. New issues are given an id on save. Without the id,
    the Comment object's own save method doesn't know where to write 
    files.

    The Issue class doesn't handle defaults for the 'author' field.
    The creator of the issue is often the web server, so we can't
    really assume anything about the acting user.
    """

    def __init__(self, tracker, id=None):
        self.fields = {
                'title'  : None,
                'status' : 'open',
                'labels' : [],
                'content': None,
                'created': None,
                'updated': None,
                'author' : {
                    'name'  : None,
                    'email' : None,
                    'avatar': None,
                    }
                }
        self.tracker = tracker
        if id is not None:
            self.id = self._resolve_id(id)
            self._set_paths()
            self.from_file(self.paths['issue'])
        super(BaseFile, self).__init__()

    def __eq__(self, other):
        return True if self.id == other.id else False

    def __ne__(self, other):
        return True if self.id != other.id else False

    def __repr__(self):
        return '<Issue %s>' % self.id[:6]

    def comments(self, n=None):
        comments = [Comment(self, sha) for sha in self._get_comments()]
        comments.sort(key=lambda x: x.timestamp)
        if n:
            return comments[:n]
        return comments

    def comment(self, sha):
        return Comment(self, sha)

    def save(self):
        """Save the issue to file."""

        # We need to set updated, even if it's the same as created,
        # so we have a consistent timestamp to sort issues by.
        self.updated = time.time()

        if not hasattr(self, 'id'):
            # IDs are generated from the JSON dump of the
            # issue. This includes the UTC-format timestamp, so 
            # they can be considered pretty unique.
            self.created = self.updated 
            self.id = get_hash(to_json(self.fields))
            # set the paths now that we have an id
            self._set_paths()
        
        # Make the parent directory if it doesn't exist.
        if not os.path.isdir(self.paths['root']):
            os.mkdir(self.paths['root'])
        # Make the comments dir if it doesn't exist.
        if not os.path.isdir(self.paths['comments']):
            os.mkdir(self.paths['comments'])
        # Save it in the db.
        self.tracker.db.insert(self)
        # Save it.
        return self.to_file(self.paths['issue'])

    def delete(self):
        """
        Delete the disk representation of the issue.

        Issues should rarely be deleted. Closed issues get hidden
        from many commands, but should still be available for reference. 
        This is here for the rare times when they need to be deleted
        (such as spam).
        """
        if not hasattr(self, 'id'):
            raise BadReference('No matching issue on disk')
        shutil.rmtree(self.paths['root'])

    @classmethod
    def revision(cls, ref=None):
        """
        Return an Issue object, representing the issue as it was in the 
        commit referenced by the given ref. The implementation will read 
        the file from its blob in the commit's tree. 

        It would be better to do a checkout, but this could be used to 
        rollback the issue, just by calling save and committing.

        NOTE that it's not doing anything with the comments. Still working
        on how that should function. 

        :param ref: a commit ref.
        :return: an Issue object.
        """
        # TODO
        raise NotImplementedError

    def revert(self, ref=None):
        """
        Does a checkout of the issue directory at the commit pointed to by
        the given ref.  After that, it will update its `fields` attribute to
        reflect any changes. Any Comment objects will need to be reinitialized. 
        """
        # TODO
        raise NotImplementedError

    def get_comment_path(self, sha):
        """Get the path to the comment with the given SHA."""
        if not hasattr(self, 'id'):
            raise BadReference('No matching issue on disk')
        return os.path.join(self.paths['comments'], sha)

    def _get_comments(self):
        """Get the SHAs of all comments to the issue."""
        if not hasattr(self, 'id'):
            raise BadReference('No matching issue on disk')
        return filter(lambda x: len(x) == 40, os.listdir(self.paths['comments']))

    def _resolve_id(self, id):
        """Resolve partial ids and verify the issue exists."""
        if len(id) == 40:
            if os.path.exists(self.tracker.get_issue_path(id)):
                return id
            else:
                raise BadReference('No matching issue on disk: %s' % id)
        # glob the path returned by the tracker helper method
        matches = glob.glob(self.tracker.get_issue_path(id + '*'))
        # no matches, raise bad ref:
        if not matches:
            raise BadReference('No matching issue on disk: %s' % id)
        # multiple matches, raise ambiguous ref:
        if len(matches) > 1:
            raise AmbiguousReference('Multiple issues matched that id fragment')
        # one match, return the match
        head = os.path.split(matches[0])[0]
        match_id = os.path.split(head)[1]
        return match_id

    def _set_paths(self):
        """
        Set paths inside the issue.

        Issue data and comments are stored in a directory named after the
        issue's SHA. 
        """
        paths = {}
        tpaths = self.tracker.paths
        # path to the issue directory
        paths['root'] = os.path.join(tpaths['issues'], self.id)
        # path to the file that holds the issue itself.
        paths['issue'] = self.tracker.get_issue_path(self.id)
        # path to the issue's comments directory.
        paths['comments'] = os.path.join(tpaths['issues'], self.id, 'comments')
        # create the comments dir if missing and the root path exists
        if not os.path.exists(paths['comments']) and os.path.exists(paths['root']):
            os.mkdir(paths['comments'])
        self.paths = paths
