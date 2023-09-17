import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from geotaste.app import get_app

def test_app_001(dash_duo):
    app = get_app()
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == [], "browser console should contain no error"