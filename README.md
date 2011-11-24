<pre>
| | | |                            
| |_| | ___  _ __  _ __   ___ _ __ 
|  _  |/ _ \| '_ \| '_ \ / _ \ '__|
| | | | (_) | |_) | |_) |  __/ |   
\_| |_/\___/| .__/| .__/ \___|_|   
            | |   | |              
            |_|   |_|              
</pre>

(Hopper is currently in development. Features are missing and it's not totally 
stable)

Hopper is a portable, distributed, version-controlled issue (AKA bug-) tracking
implementation. It's quite a mouthful. 

It comes with a web application, command-line interface, and the core API.

How it works
------------
For every project, you have a completely self-contained issue tracker. The 
tracker is a Git repository. Hopper handles all the versioning for you. Issues
and comments are stored in a flat-file database as JSON, making them both ideal 
for merging and human-editable. 

For the full spiel, see the API documentation.

Use cases
---------
There are many ways to use Hopper:

- Host the web application on a central server, like many traditional issue 
  trackers. Users login to the web application.
- Host the git repository on a central server. Users can push and pull,
  viewing issues locally with the web or CLI client.
- Pull directly from other developers. Users run the clients locally.
- Keep your issues all to yourself. Run the clients locally.
- **...any mix of the above.**

Why
---
Distributed workflows allow us to work locally and offline. Anyone who's moved
from SVN to Git or Mercurial understands these benefits.

There are also a lot of interesting things you can do with version control.
When you fork a project, you can fork the issue tracker too. Merge them back
together later.
