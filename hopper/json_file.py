from __future__ import with_statement
import os

from hopper.base_file import BaseFile
from hopper.utils import from_json, to_json

class JSONFile(BaseFile):
    '''
    JSONFile subclasses the BaseFile class to provide methods
    for reading and writing JSON to file.
    '''

    def from_file(self, f):
        '''Read self.fields from file.'''
        if not os.path.exists(f):
            raise OSError('File does not exist')
        with open(f, 'r') as fp:
            self.fields = from_json(fp.read())
        return True

    def to_file(self, f):
        '''Save self.fields to file.'''
        if not type(self.fields) is dict:
            raise TypeError('self.fields must be a dict')
        with open(f, 'w') as fp:
            fp.write(to_json(self.fields))
        return True
