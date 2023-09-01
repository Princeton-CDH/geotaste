from geotaste.imports import *

def get_app():
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
        )
        return app

def get_server():
    app = get_app()
    return app.app.server

def run(host=HOST, port=PORT, debug=DEBUG, **kwargs):
    app = get_app()
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