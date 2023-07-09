from geotaste2.imports import *
from geotaste2 import __version__


def run(host=HOST, port=PORT, debug=DEBUG, **kwargs):
    with Logwatch(f'booting geotaste v{__version__}'):
        layout = GeotasteLayout()        
        app = DashApp(
            layout, 
            bootstrap=True,
            meta_tags=[{
                "name": "viewport",
                "content": "width=device-width, initial-scale=1"
            }],
            assets_folder=PATH_ASSETS,
        )
        server = app.app.server

    with Logwatch('running app'):
        logger.debug(f'geotaste running at http://{host}:{port}')
        app.run(
            host=host,
            port=port,
            debug=debug,
            **kwargs
        )
    return server

def run_debug(host=HOST, port=PORT, debug=True, **kwargs):
    return run(host=host,port=port,debug=debug,**kwargs)

def run_safe(host=HOST, port=PORT, debug=False, **kwargs):
    return run(host=host,port=port,debug=debug,**kwargs)

if __name__=='__main__': run()