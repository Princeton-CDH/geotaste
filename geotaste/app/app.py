from ..imports import *


def run():
    print('booting')

    # layout = GeotasteLayout()
    layout = MemberPanel()
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
    app.run(
        8111, 
        host='0.0.0.0',
        debug=True,
        # dev_tools_ui=False
    )
    return server

if __name__=='__main__': run()