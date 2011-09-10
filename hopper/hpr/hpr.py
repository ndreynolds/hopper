from argparse import ArgumentParser
import sys
import os

# hopper imports
from hopper.tracker import Tracker
from hopper.issue import Issue
from hopper.config import Config
from hopper.web.main import start
from hopper.hpr.templates import IssueTemplate

# utilities
def get_tracker(path=None):
    '''Get the tracker or raise an error.'''
    if path is None:
        cwd = os.getcwd()
        if is_tracker(cwd):
            return Tracker(cwd)
        else:
            raise OSError('The cwd is not a Hopper tracker')
    elif os.path.exists(path) and is_tracker(path):
        return Tracker(path)
    raise OSError('The supplied path is not a Hopper tracker')

def is_tracker(path):
    '''Check if the given path is a Hopper tracker'''
    # This is only a good guess. Corrupt trackers will fail to init.
    dirlist = os.listdir(path)
    return '.hopper' in dirlist and '.git' in dirlist

def main():
    '''Parse the sys args using argparse and call the appropriate function'''
    parser = ArgumentParser(description='Manage Hopper trackers and their issues', 
                            prog='hpr')
    parser.add_argument('-v', '--version', action='version', version='1.0')
    parser.add_argument('-t', '--tracker', action='store')
    subparsers = parser.add_subparsers(help='sub-command help')
    
    # `new` subcommand
    newp = subparsers.add_parser('new', help='Create a new issue')
    newp.add_argument('-e', '--editor', action='store',
            help='use the given editor')
    newp.add_argument('-m', '--message', action='store', 
            help='use the given message instead of opening the editor')
    newp.set_defaults(func=new)

    # `edit` subcommand
    editp = subparsers.add_parser('edit', help='Edit an existing issue')
    editp.add_argument('issue', help='an issue id (the first 4 chars is usually enough)')
    editp.set_defaults(func=edit)

    # `serve` subcommand
    servep = subparsers.add_parser('serve', help='Serve a web interface \
            to the tracker')
    servep.add_argument('-p', '--port', action='store', 
                        help='serve on the specified prot, default is 5000')
    servep.add_argument('-v', '--verbose', action='store_true', 
                        help='turn on debug mode')
    servep.set_defaults(func=serve)

    # `tracker` subcommand
    trackerp = subparsers.add_parser('tracker', help='Create a new hopper tracker')
    trackerp.add_argument('path', action='store', 
                        help='path that the tracker will be created at')
    trackerp.set_defaults(func=tracker)

    # parse the args
    args = parser.parse_args(sys.argv[1:])
    argsd = vars(args)

    # replace argsd['tracker'] with a Tracker instance.
    if args.func != tracker:
        argsd['tracker'] = get_tracker(argsd['tracker'])
    args.func(argsd)

### Manage issues
def new(args):
    i = Issue(args['tracker'])
    conf = Config()
    if args['message'] is not None:
        i.title = args['message']
        i.content = '.'
        if i.save():
            print 'Created issue %s' % i.id
    editor = args['editor'] if args['editor'] else conf.core['editor']
    # the Template object opens templates in the editor and parses them.
    template = IssueTemplate('new.hpr')
    path = template.open(editor)
    fields = template.parse(path)
    i.title = fields['title']
    i.content = fields['content']
    if i.save():
        print 'Created issue %s' % i.id

def edit(args):
    t = args['tracker']
    i = t.issue(args['issue'])
    if not i:
        print 'No such issue'
        return

def reopen(args):
    t = args['tracker']
    i = t.issue(args['issue'])
    if not i:
        print 'No such issue'
        return
    if i.status == 'closed':
        i.status = 'open'
        i.save()
    else:
        print 'Already open'

def close(args):
    t = args['tracker']
    i = t.issue(args['issue'])
    if not i:
        print 'No such issue'
        return
    if i.status == 'open':
        i.status = 'closed'
        i.save()
    else:
        print 'Already closed'

def show(args):
    t = args['tracker']
    i = t.issue(args['issue'])
    if not i:
        print 'No such issue'
        return
    print i.title
    print i.content

### Manage trackers
def serve(args):
    t = args['tracker']
    start(t.paths['root'], port=args['port'], debug=args['verbose'])

def tracker(args):
    Tracker.new(args['path'])
    print 'New tracker initialized. Edit %s to configure.' % \
            os.path.join(args['path'], 'config') 

def lock_on(args):
    print 'lock-on'

def comment(args):
    print 'comment'

if __name__ == '__main__':
    main()
