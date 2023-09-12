from geotaste.imports import *

def get_app(url_base_pathname=ROOT_URL):
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
    app = get_app()
    return app.app.server

def run(host=HOST, port=PORT, debug=DEBUG, url_base_pathname=ROOT_URL, **kwargs):
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

def run_debug(host=HOST, port=PORT, debug=True, **kwargs):
    return run(host=host,port=port,debug=debug,**kwargs)

def run_safe(host=HOST, port=PORT, debug=False, **kwargs):
    return run(host=host,port=port,debug=debug,**kwargs)

if __name__=='__main__': run()