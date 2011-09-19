from argparse import ArgumentParser
import sys
import os

# hopper imports
from hopper.tracker import Tracker
from hopper.issue import Issue
from hopper.comment import Comment
from hopper.config import Config
from hopper.web.manage import start
from hopper.hpr.templates import Template, IssueTemplate
from hopper.utils import relative_time, wrap


### utilities
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


### main script (arg parser)
def main(args=sys.argv[1:]):
    ''' 
    Parse the sys args using argparse and call the appropriate function.

    :param args: arguments to use. This defaults to sys.argv[1:] (the sys
                 arguments after the command itself). Supplying a list for
                 args lets you call hpr commands from within python, for
                 whatever reason.
    ''' 
    parser = ArgumentParser(description='Manage Hopper trackers and their issues', 
                            epilog='See `hpr COMMAND -h` for command-specific help',
                            prog='hpr')
    parser.add_argument('-v', '--version', action='version', version='1.0',
            help='display version number')
    parser.add_argument('--tracker', action='store', metavar='PATH',
            help='set the path to the tracker, defaults to cwd')
    subparsers = parser.add_subparsers(title='commands')
    
    # `comment` subcommand
    commentp = subparsers.add_parser('comment', help='Comment on an issue')
    commentp.add_argument('issue', 
            help='an issue id (the first 4 chars is usually enough)')
    commentp.add_argument('-e', '--editor', action='store', 
            help='use the given editor')
    commentp.set_defaults(func=comment)

    # `edit` subcommand
    editp = subparsers.add_parser('edit', help='Edit an existing issue')
    editp.add_argument('issue', help='an issue id (the first 4 chars is usually enough)')
    editp.set_defaults(func=edit)

    # `list` subcommand
    listp = subparsers.add_parser('list', 
            help='List the (filtered) set of issues')
    listp.add_argument('-s', '--short', action='store_true', 
            help='display each issue in one line')
    listp.add_argument('-v', '--verbose', action='store_true',
            help="show each issue's content")
    listp.add_argument('-vv', '--super-verbose', action='store_true',
            help="show each issue's content and comments")
    listp.set_defaults(func=list_)

    # `new` subcommand
    newp = subparsers.add_parser('new', help='Create a new issue')
    newp.add_argument('-e', '--editor', action='store',
            help='use the given editor')
    newp.add_argument('-m', '--message', action='store', 
            help='use the given message instead of opening the editor')
    newp.set_defaults(func=new)

    # `serve` subcommand
    servep = subparsers.add_parser('serve', help='Serve a web interface \
            to the tracker')
    servep.add_argument('-p', '--port', action='store', 
                        help='serve on the specified prot, default is 5000')
    servep.add_argument('-v', '--verbose', action='store_true', 
                        help='turn on debug mode')
    servep.set_defaults(func=serve)

    # `show` subcommand
    showp = subparsers.add_parser('show', help='Show a particular issue')
    showp.add_argument('issue', help='an issue id (the first 4 chars is usually enough)')
    showp.set_defaults(func=show)

    # `tracker` subcommand
    trackerp = subparsers.add_parser('tracker', help='Create a new hopper tracker')
    trackerp.add_argument('path', action='store', 
                        help='path that the tracker will be created at')
    trackerp.set_defaults(func=tracker)

    # parse the args
    args = parser.parse_args(args)
    argsd = vars(args)

    # replace argsd['tracker'] with a Tracker instance.
    if args.func != tracker:
        argsd['tracker'] = get_tracker(argsd['tracker'])
    args.func(argsd)


### Command functions

# Manage issues
def new(args):
    '''Create a new issue.'''
    i = Issue(args['tracker'])
    conf = Config()
    # set the author info
    i.author['name'] = conf.user['name']
    i.author['email'] = conf.user['email']
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
        print 'Created issue %s' % i.id[:6]

def edit(args):
    '''Edit an existing issue'''
    t = args['tracker']
    i = t.issue(args['issue'])
    if not i:
        print 'No such issue'
        return

def comment(args):
    '''Comment on an issue.'''
    t = args['tracker']
    i = t.issue(args['issue'])
    if not i:
        print 'No such issue'
        return
    c = Comment(i)
    conf = Config()
    # set the author info
    c.author['name'] = conf.user['name']
    c.author['email'] = conf.user['email']
    editor = args['editor'] if args['editor'] else conf.core['editor']
    template = Template('comment.hpr')
    path = template.open(editor)
    fields = template.parse(path)
    c.content = fields['content']
    if c.save() and i.save():
        print 'Posted comment %s on issue %s' % (c.id[:6], i.id[:6])

def reopen(args):
    '''Reopen a closed issue.'''
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
    '''Close an open issue.'''
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
    '''Show an issue.'''
    t = args['tracker']
    i = t.issue(args['issue'])
    c = Config()
    if not i:
        print 'No such issue'
        return
    print '%s %s' % (c.decorate('red', 'issue'), i.id)
    print '%s  %s <%s>' % (c.decorate('yellow', 'Author:'), i.author['name'], i.author['email'])
    print '%s %s' % (c.decorate('yellow', 'Created:'), relative_time(i.created))
    if i.updated != i.created:
        print '%s %s' % (c.decorate('yellow', 'Updated:'), relative_time(i.updated))
    print '%s  %s' % (c.decorate('yellow', 'Status:'), i.status)
    print
    print '    ' + c.decorate('bold', i.title)
    print
    content = wrap(i.content)
    for line in content.splitlines():
        print '    ' + line
    print

def list_(args):
    '''List the tracker's issues (filtered by criteria)'''
    t = args['tracker']
    c = Config()
    issues = t.issues()
    # short mode
    if args['short']:
        for i in issues:
            print '%s %s' % (c.decorate('red', i.id[:6]), i.title)
    # verbose mode
    elif args['verbose']:
        for i in issues:
            print '%s %s' % (c.decorate('red', 'issue'), i.id)
            print '%s  %s <%s>' % (c.decorate('yellow', 'Author:'), i.author['name'], i.author['email'])
            print '%s %s' % (c.decorate('yellow', 'Created:'), relative_time(i.created))
            if i.updated != i.created:
                print '%s %s' % (c.decorate('yellow', 'Updated:'), relative_time(i.updated))
            print '%s  %s' % (c.decorate('yellow', 'Status:'), i.status)
            print
            print '    ' + c.decorate('bold', i.title)
            print
            content = wrap(i.content)
            for line in content.splitlines():
                print '    ' + line
            print
    # normal mode
    else:
        for i in issues:
            print '%s %s' % (c.decorate('red', 'issue'), i.id)
            print '%s %s <%s>' % (c.decorate('yellow', 'Author:'), i.author['name'], i.author['email'])
            print '%s %s' % (c.decorate('yellow', 'Created:'), relative_time(i.created))
            if i.updated != i.created:
                print '%s %s' % (c.decorate('yellow', 'Updated:'), relative_time(i.updated))
            print
            print '    ' + i.title
            print

# Manage trackers
def serve(args):
    t = args['tracker']
    start(t.paths['root'], port=args['port'], debug=args['verbose'])

def tracker(args):
    Tracker.new(args['path'])
    print 'New tracker initialized. Edit %s to configure.' % \
            os.path.join(args['path'], 'config') 


if __name__ == '__main__':
    main()
