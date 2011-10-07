# For development, will use the local repo instead of the installed package.
# It will fallback to the installed package anyway, so it's not a big deal
# if the path doesn't exist.
import sys
import os
home = os.getenv('HOME')
sys.path.insert(0, os.path.join(home, 'repos/hopper'))
from hopper.web.app import app

def start(path, port=5000, debug=False, external=False):
    '''
    Run the Hopper tracker at the given path. Allows for setting the port,
    debug mode, and whether or not it's externally visible. 

    Running it on port 80 is possible but will usually require being root.
    '''

    # Try and get an int out of the port param, set to 5000 if anything
    # goes wrong.
    app.GLOBALS['tracker'] = path
    if type(port) in [int, str]:
        try:
            port = int(port)
        except ValueError:
            port = 5000
    else:
        port = 5000
    if external:
        # Run the app on a public IP. Debug will be off.
        app.debug=False
        app.run(host='0.0.0.0', port=port)
    else:
        # Run the app on the localhost.
        app.debug = debug
        app.run(port=port)

if __name__ == '__main__':
    start(os.path.join(home, 'trackers/hopper2'), debug=True)
