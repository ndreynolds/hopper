from __future__ import with_statement
from flask import Flask
from hopper.config import UserConfig

# Create the app
app = Flask(__name__)

# Get the Secret Key from the user onfig
c = UserConfig()
app.secret_key = c.web['secret_key']

# We need to share a few vars between scripts:
app.GLOBALS = {
        'debug': True,
        'first_request': True, # give the user a env context msg
        }

# Import blueprints
from hopper.web.views.issues import issues
from hopper.web.views.docs import docs
from hopper.web.views.feed import feed

# Register blueprints
app.register_blueprint(issues, url_prefix='/issues')
app.register_blueprint(docs, url_prefix='/docs')
app.register_blueprint(feed)
