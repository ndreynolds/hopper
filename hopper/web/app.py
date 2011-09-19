from flask import Flask

# Create the app
app = Flask(__name__)
app.secret_key = 'sdgasd6t4ry43y45SADGVQ43Y345RQw356y45sDGDSgSDG'

# We need to share a few vars between scripts:
GLOBALS = {
        'debug': True,
        'first_request': True, # give the user a env context msg
        'tracker': None 
        }

# Import and register modules
from hopper.web.views.issues import issues
from hopper.web.views.project import project
app.register_module(issues, url_prefix='/issues')
app.register_module(project)
