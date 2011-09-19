from __future__ import with_statement
import hashlib
import time
import os
from flask import Flask

# Create the app
app = Flask(__name__)

# Look for a SECRET_KEY file, or make one.
path = os.path.split(__file__)[0]
path = os.path.join(path, 'SECRET_KEY')
try:
    with open(path, 'r') as fp:
        key = fp.read()
except IOError:
    key = hashlib.sha1(str(time.time()))
    with open(path, 'w') as fp:
        fp.write(key)

app.secret_key = key

# We need to share a few vars between scripts:
app.GLOBALS = {
        'debug': True,
        'first_request': True, # give the user a env context msg
        'tracker': None 
        }

# Import blueprints
from hopper.web.views.issues import issues
from hopper.web.views.project import project

# Register blueprints
app.register_blueprint(issues, url_prefix='/issues')
app.register_blueprint(project)
