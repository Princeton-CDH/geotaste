import diskcache

import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from geotaste.imports import *
from geotaste.app import *
import webview

HOSTPORTURL=f'http://{HOST}:{PORT}'

@cache
def get_app_global():
    return get_app()


def mainview(**kwargs):
    # view(**kwargs)
    # main(**kwargs)
    res=browse(func = main)
    print(res)


def main(debug=DEBUG, **kwargs): 
    app=get_app_global()
    app.run(host=HOST, port=PORT, debug=debug)



def browse(**kwargs):
    app=get_app_global()
    try:
        from screeninfo import get_monitors
        m = get_monitors()[0]
        width = m.width
        height = m.height
    except Exception:
        width = 1400
        height = 1100

    with app.app.server.app_context():
        webview.create_window(
            title=WELCOME_HEADER, 
            url=f'http://{HOST}:{PORT}/sco/1',
            fullscreen=False,
            width=width,
            height=height,
            min_size=(400,300),
            frameless=False,
            easy_drag=True,
            text_select=True,
            confirm_close=True,
        )
        return webview.start(
            private_mode=False,
            storage_path=PATH_SRVR,
            debug=True,
            **kwargs
        )



def run():
    return mainview(debug=False)


if __name__=='__main__': 
    run()