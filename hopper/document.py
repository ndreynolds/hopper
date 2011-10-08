from __future__ import with_statement
import os

from hopper.files import lock
from hopper.utils import markdown_to_html, rst_to_html

class Document(object):
    '''
    The Document object represents a documentation file. It's a fairly 
    thin wrapper around reading and writing the file, and converting it
    to HTMl from Markdown or reST. The LockedFile class is used for file
    I/O.

    :param tracker: the tracker that owns the document.
    :param path: the path relative to the tracker's `docs` directory.
                 This will usually just be the basename (unless the docs
                 are nested into subdirectories).
    '''

    def __init__(self, tracker, path):
        self.path = os.path.join(tracker.paths['docs'], path)
        # link (basename, no ext, contains '-'s)
        self.link = os.path.splitext(path)[0]
        # ext (e.g. '.md' or '.rst')
        self.ext = os.path.splitext(path)[1]
        # name (basename, no ext, '-'s stripped)
        self.name = self.link.replace('-', ' ')
        if not os.path.isfile(self.path):
            raise OSError('Document does not exist.')
    
    def read(self, convert=False):
        '''
        Read the file (after acquiring a lock).

        :param convert: if the content is Markdown or reST (based
                        on the file extension) attempt to convert it
                        first.
        :return: string containing file contents.
        '''
        with lock(self.path, 'r') as fp:
            content = fp.read()
        if convert:
            if self.ext[1:] in ['md', 'mdown', 'markdown', 'mdwn']:
                return markdown_to_html(content)
            elif self.ext[1:] == 'rst':
                return rst_to_html(content)
        return content

    def write(self, text):
        '''
        Write the file (after acquiring a lock).

        :param text: string to write to the file.
        '''
        with lock(self.path, 'w') as fp:
            fp.write(text)
