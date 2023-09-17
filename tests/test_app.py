import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from geotaste.app import get_app

from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--window-size=1420,1080')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=chrome_options)


def test_app_001(dash_duo):
    app = get_app()
    dash_duo.start_server(app)
    assert dash_duo.get_logs() == [], "browser console should contain no error"