"""
This module contains the few functions we need to start and run the Dash app. 

Note: Because we're using Dash OOP components, we instantiate a `DashApp` object, whose `app` attribute is the `dash.Dash` app object.
"""
from geotaste.imports import *

def get_app(url_base_pathname=ROOT_URL):
    """Returns a DashApp object with specified configurations.
    
    Args:
        url_base_pathname (str): The base URL pathname for the app. Defaults to ROOT_URL. Could be "/sco/1" for instance. This can be set in ~/geotaste_data/config.json under ROOT_URL.
    
    Returns:
        app (DashApp): The DashApp object with specified configurations.
    """
    if not url_base_pathname.endswith('/'):
        url_base_pathname+='/'
    with Logwatch(f'booting geotaste'):
        layout = GeotasteLayout()        
        app = DashApp(
            layout, 
            bootstrap=True,
            meta_tags=[{
                "name": "viewport",
                "content": "width=device-width, initial-scale=1"
            }],
            assets_folder=PATH_ASSETS,
            suppress_callback_exceptions=True,
            url_base_pathname=url_base_pathname,
        )
        app.app.config.suppress_callback_exceptions=True
        return app

def get_server():
    """Returns the server object from the Flask app.
    
    Returns:
        server (object): The server object from the Flask app.
    """
    app = get_app()
    return app.app.server

def run(host=HOST, port=PORT, debug=DEBUG, url_base_pathname=ROOT_URL, **kwargs):
    """Runs the geotaste app on the specified host and port. The constants mentioned below can be overwritten/set in ~/geotaste_data/config.json.
    
    Args:
        host (str): The host address to run the app on. Defaults to HOST.
        port (int): The port number to run the app on. Defaults to PORT.
        debug (bool): Whether to run the app in debug mode. Defaults to DEBUG.
        url_base_pathname (str): The base URL pathname for the app. Defaults to ROOT_URL.
        **kwargs: Additional keyword arguments to be passed to the app.run() method.
    
    Returns:
        flask.Flask: The Flask app server object.
    
    Examples:
        # Run the app on the default host and port
        run()
    
        # Run the app on a specific host and port
        run(host='0.0.0.0', port=8080)
    
        # Run the app in debug mode
        run(debug=True)
    """
    
    app = get_app(url_base_pathname=url_base_pathname)
    with Logwatch('running app'):
        logger.debug(f'geotaste running at http://{host}:{port}')
        app.run(
            host=host,
            port=port,
            debug=debug,
            **kwargs
        )
    return app.app.server

if __name__=='__main__': run()