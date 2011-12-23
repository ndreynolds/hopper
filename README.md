<pre>
| | | |                            
| |_| | ___  _ __  _ __   ___ _ __ 
|  _  |/ _ \| '_ \| '_ \ / _ \ '__|
| | | | (_) | |_) | |_) |  __/ |   
\_| |_/\___/| .__/| .__/ \___|_|   
            | |   | |              
            |_|   |_|              
</pre>

Hopper is a portable, distributed, version-controlled issue (AKA bug-) tracking
implementation. 

Hopper comes with web and command-line clients. Here they are in action:

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
the docs yourself using Sphinx.)

Running Hopper
--------------
Hopper can be run locally (optionally using Git to push, pull, and clone)

#### Local 
Users run the web and CLI clients locally on trackers in the local filesystem.

#### Git Server
Users run the web and CLI clients locally on trackers cloned from a central 
server. They can push and pull to update the tracker.

#### Web
Users access the web client, running on a remote server, over the web. All 
changes are made to a single tracker instance. This is how traditional issue
trackers work.
