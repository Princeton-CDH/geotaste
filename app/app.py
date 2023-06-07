from app_imports import *
from app_figs import *
from app_widgets import *
from app_components import *
    

if __name__=='__main__':
    layout = GeotasteLayout()
    app = DashApp(layout, bootstrap=True)
    app.run(8052)