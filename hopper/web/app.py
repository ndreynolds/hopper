from __future__ import with_statement
import hashlib
import time
import os
from flask import Flask
from hopper.config import Config

# Create the app
app = Flask(__name__)

# Get the Secret Key from Config
c = Config()
app.secret_key = c.web['secret_key']

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
