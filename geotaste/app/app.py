from ..imports import *
from .layouts import GeotasteLayout

def run():
    layout = GeotasteLayout()
    app = DashApp(
        layout, 
        bootstrap=True,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
        assets_folder=PATH_ASSETS,
    )
    # move to here
    # app.run(8052, host='0.0.0.0')
    print('booting')
    app.run(8053, debug=True, dev_tools_ui=False, dev_tools_hot_reload=True)

if __name__=='__main__': run()