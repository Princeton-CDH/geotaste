from .imports import *

PATH_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

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
    app.run(8052)

if __name__=='__main__': run()