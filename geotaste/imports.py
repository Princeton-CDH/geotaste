import os,sys
path_here = os.path.abspath(os.path.dirname(__file__))
path_home = os.path.expanduser('~')
path_data = os.path.abspath(os.path.join(path_home,'geotaste_data'))
try:
    if not os.path.exists(path_data):
        os.makedirs(path_data)
except Exception:
    pass

# Paths
paths=dict(
    here=path_here,
    data=path_data,
    members = os.path.join(path_data,'members.csv'),
    books = os.path.join(path_data,'books.csv'),
    events = os.path.join(path_data,'events.csv'),
)

# Three datasets
urls = dict(
    members = 'https://dataspace.princeton.edu/bitstream/88435/dsp01dv13zx35z/2/SCoData_members_v1.2_2022-01.csv',
    books = 'https://dataspace.princeton.edu/bitstream/88435/dsp01jm214s28p/2/SCoData_books_v1.2_2022-01.csv',
    events = 'https://dataspace.princeton.edu/bitstream/88435/dsp019306t2441/2/SCoData_events_v1.2_2022-01.csv',
)

# Synthesized
url_gsheet = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRPt6EM6c2O8D566ctN3_dmPjxqEKmegBpcHzLCPLNZoNFkiiH9JWisbFB_DDrEnQM4JT8wytc_iL5Y/pub?gid=0&single=true&output=csv'


## other vars
latlon_SCO = (48.85107555543428, 2.3385039932538567)



## imports
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import folium
from functools import lru_cache as cache
import numpy as np
from collections import Counter
from pprint import pprint,pformat
from ipywidgets import Dropdown, interact, interactive
from folium.plugins import HeatMap
from IPython.display import display, HTML
import requests,json
from ipywidgets import *
from IPython.display import Markdown, HTML, clear_output

