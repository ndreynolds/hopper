from __future__ import with_statement
import os
import tempfile

from hopper.files import lock

class Template(object):
    def __init__(self, template):
        if not os.path.exists(template):
            parent = os.path.split(__file__)[0]
            tpath = os.path.join(parent, 'hpr_templates', template)
            if os.path.exists(tpath):
                template = tpath
            else:
                raise OSError('The template, %s, does not exist' % template)
        with open(template, 'r') as fp:
            self.template = fp.read()

    def open(self, editor):
        """
        Create a temp file, write the contents of self.template to it,
        and open it with the given editor.
        """
        if not self._is_exec(editor):
            raise OSError('%s is not executable. Provide an executable \
                    editor in your .hprconfig' % editor)
        temp = tempfile.mkstemp(suffix='.hpr')[1]
        # don't need locking here.
        with open(temp, 'w') as fp:
            fp.write(self.template)
        os.system('%s %s' % (editor, temp))
        return temp 

    def parse(self, path):
        """Basic parser, returns all lines that don't start with #"""
        with open(path, 'r') as fp:
            lines = fp.read().splitlines()
        parsed = '\n'.join(l for l in lines if not l.startswith('#'))
        return {'content': parsed}

    def _is_exec(self, editor):
        """Determine if the editor is present and executable."""
        for path in os.environ['PATH'].split(os.pathsep):
            exe = os.path.join(path, editor)
            if os.path.exists(exe) and os.access(exe, os.X_OK):
                return True
        return False

class IssueTemplate(Template):
    def parse(self, path):
        """
        Parse an issue template ('new' or 'edit'). The rules:
            * first line is the title, first char may not be ' '.
            * next non-blank line -> EOF is the content
            * lines starting with '#' are ignored.
        """
        fields = {}
        with open(path, 'r') as fp:
            lines = fp.read().splitlines()
        # remove comment lines.
        lines = [l for l in lines if not l.startswith('#')]
        # abort if the first line is empty.
        if not lines[0].strip():
            print 'Aborted due to empty first line'
            raise SystemExit
        # get the title
        fields['title'] = lines[0]
        # extract the content, starting with line 2 if line 1 is blank
        try:
            if not lines[1].strip():
                fields['content'] = '\n'.join(lines[2:])
            else:
                fields['content'] = '\n'.join(lines[1:])
        except IndexError:
            # if we ran into an index error, we don't have the content 
            # field and need to abort.
            print "Aborted due to empty issue content."
            raise SystemExit
        return fields
