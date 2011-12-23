<pre>
| | | |                            
| |_| | ___  _ __  _ __   ___ _ __ 
|  _  |/ _ \| '_ \| '_ \ / _ \ '__|
| | | | (_) | |_) | |_) |  __/ |   
\_| |_/\___/| .__/| .__/ \___|_|   
            | |   | |              
            |_|   |_|              
</pre>

Hopper is a portable, distributed, version-controlled issue tracking
implementation. It's sort of an experiment on distributed editing in CMS-type 
applications.

It is currently in development and not ready for real use.

Hopper comes with web and command-line clients. Here's the web UI in action:

[photos]

How it works
------------
For every project, you have a completely self-contained issue tracker. Issues
and comments are stored within the tracker in a flat-file database as JSON. To
implement versioning, the tracker is also a full-fledged Git repository. Hopper 
handles all the Git interaction for you, so you don't need to know anything 
about Git. 

Most of the time, users would work on issues from a single tracker instance.
This way everything is live. Sometimes, though, you know you'll be without 
internet access, so Hopper allows you to clone the tracker's repository and
work locally, merging things back together later.

For the full spiel, see the API documentation. (Currently, you'll need to build
the docs yourself using [Sphinx][1].)

Installing
----------
Clone the repo and run `setup.py`:

    git clone https://ndreynolds@github.com/ndreynolds/hopper.git
    cd hopper/
    sudo python setup.py install

Using it
--------
Trackers can be interfaced with locally through either client (optionally using 
Git to share changes with remote instances) or over HTTP through the web client.

Being able to treat the trackers just like any other Git repository makes for a 
lot of interesting use-cases. One example would be to make the tracker available
on a git server and provide it as a Git submodule within the project repository.
Everyone that has the repo gets the whole as issue tracker as a freebie.

[1]: http://sphinx.pocoo.org/
