from app_imports import *
from app_figs import *
from app_widgets import *
from app_components import *
    

if __name__=='__main__':
    layout = GeotasteLayout()
    app = DashApp(
        layout, 
        bootstrap=True,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ]
    )
    app.run(8052)