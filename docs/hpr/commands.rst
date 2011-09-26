=================
Command Reference
=================

**Positional** arguments are required, while **optional** arguments are
just that, optional. 

Keep in mind that tracker issues are referred to by their SHA1 unique 
identifiers. You only need to supply as many characters as necessary to
make the reference unique.

``hpr`` options and arguments
=============================

**Usage**::

    $ hpr [subcommand] [(args)]

**Optional Arguments:**

* ``-v``, ``--version`` -- display version number.
* ``-h``, ``--help`` -- display help information.
* ``--tracker`` -- set the path to the tracker, defaults to cwd. Same
  idea as Git's ``--git-dir`` option.
 

Subcommands
===========

comment
-------
Comment on an issue.

**Usage**::

    $ hpr comment [issue]
    [in editor]

**Positional Arguments**:

* ``issue`` -- an issue identifier

**Optional Arguments**:

* ``-e``, ``--editor`` -- the editor to use.


close
-----
Close an open issue.

**Usage**::

    $ hpr close [issue]

**Positional Arguments**:

* ``issue`` -- an issue identifier


edit
----
Edit an issue.

**Usage**::

    $ hpr edit [issue]
    [in editor]

**Positional Arguments**:

* ``issue`` -- an issue identifier

**Optional Arguments**:

* ``-e``, ``--editor`` -- the editor to use.


list
----
List the tracker's issues, optionally filtered by criteria.

**Usage**::

    $ hpr list

**Optional Arguments**:

* ``-s``, ``--short`` -- display each issue in a single line.
* ``-v``, ``--verbose`` -- show each issue's content.
* ``-vv``, ``--super-verbose`` -- show each issue's content and comments.

Note that ``-s``, ``-v``, and ``-vv`` are mutually-exclusive. The first flag
found (looking in the order above) is used.


new
---
Create an issue.

**Usage**::

    $ hpr new
    [in editor]

**Optional Arguments**:

* ``-e``, ``--editor`` -- the editor to use.
* ``-m``, ``--message`` -- supply the issue's summary inline, with no content.


reopen
------
Reopen a closed issue.

**Usage**::

    $ hpr reopen [issue]

**Positional Arguments**:

* ``issue`` -- an issue identifier


serve
-----
Serve a web interface to a tracker on a local port.

**Usage**::

    $ hpr serve

**Optional Arguments**:

* ``-p``, ``--port`` -- serve on the specified port, defaults to 5000.
* ``-v``, ``--verbose`` -- turn on debug mode. This option is ignored if
  you're serving on a non-public IP.


show
----
Show an issue and its comments.

**Usage**::

    $ hpr show [issue]

**Positional Arguments**:

* ``issue`` -- an issue identifier


tracker
-------
Create a tracker.

**Usage**::

    $ hpr tracker [path]

**Positional Arguments**:

* ``path`` -- a path, absolute or relative to your current working 
  directory, to create a new tracker directory and repository at.
  Same idea as ``mkdir [path]``.
