from ..imports import *
from .layouts import GeotasteLayout


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

def run():
    print('booting')
    app.run(
        8111, 
        host='0.0.0.0',
        debug=True
    )

if __name__=='__main__': run()