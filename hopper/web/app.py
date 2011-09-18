from flask import Flask

app = Flask(__name__)
app.secret_key = 'sdgasd6t4ry43y45SADGVQ43Y345RQw356y45sDGDSgSDG'
GLOBALS = {
        'debug': True,
        'first_request': True,
        'tracker': None
        }

# Import and register modules
from hopper.web.views.issues import issues
from hopper.web.views.project import project
app.register_module(issues, url_prefix='/issues')
app.register_module(project)
