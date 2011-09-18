from hopper.web.app import app, GLOBALS

def start(path, port=5000, debug=False, external=False):
    '''
    Run the Hopper tracker at the given path. Allows for setting the port,
    debug mode, and whether or not it's externally visible. 

    Running it on port 80 is possible but will usually require being root.
    '''
    # Try and get an int out of the port param, set to 5000 if anything
    # goes wrong.
    global GLOBALS
    GLOBALS['tracker'] = path
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
    start('/Users/ndreynolds/trackers/hopper', debug=True)
