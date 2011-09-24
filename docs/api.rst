API
===
This covers Hopper's core API. 

**Overview:**

The bulk of the issue tracking is implemented with 3 classes:

* ``Tracker`` -- Tracks issues for a single project. Trackers have many issues.
* ``Issue`` -- Represents an issue with various fields. Issues have many comments.
* ``Comment`` -- Represents a comment on an issue with various fields.

The ``hopper.files`` module contains classes for abstracting the reading and 
writing of Python dictionaries to and from various formats. For example, the
``JSONFile`` class is subclassed by the ``Issue`` and ``Comment`` classes.

The ``hopper.git`` module provides high-level Git access (through Dulwich). Hopper
relies on the Git repository for history and its distributed workflow. It is used 
primarily by the ``Tracker`` class.

Files
-----

.. automodule:: hopper.files
   :members:

Tracker
-------

.. automodule:: hopper.tracker
   :members:

Issue
-----

.. automodule:: hopper.issue
   :members:

Comment
-------

.. automodule:: hopper.comment
   :members:

Git Interaction
---------------

.. automodule:: hopper.git
   :members:


