from __future__ import with_statement
import os

from hopper.files import lock

class Document(object):
    '''
    The Document object represents a documentation file. It's a fairly 
    thin wrapper around reading and writing the file. 

    :param tracker: the tracker that owns the document.
    :param path: the path relative to the tracker's `docs` directory.
                 This will usually just be the basename (unless the docs
                 are nested into subdirectories).
    '''

    def __init__(self, tracker, path):
        self.path = os.path.join(self.tracker.paths['docs'], path)
        if not os.path.isfile(self.path):
            raise OSError('Document does not exist.')
    
    def read(self):
        '''
        Read the file (after acquiring a lock).

        :return: string containing file contents.
        '''
        with lock(self.path, 'r') as fp:
            return fp.read()

    def write(self, text):
        '''
        Write the file (after acquiring a lock).

        :param text: string to write to the file.
        '''
        with lock(self.path, 'w') as fp:
            fp.write(text)
