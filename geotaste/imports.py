## Constants

# LEFT_COLOR='#7d6ab6'
# RIGHT_COLOR='#1a6b47'
# BOTH_COLOR='#354469'

# LEFT_COLOR='#bf6927'
# RIGHT_COLOR='#221fb5'
# BOTH_COLOR='#2f9c76'

LEFT_COLOR='#7d6ab6'
RIGHT_COLOR='#bf6927'
BOTH_COLOR='#606060'


EXTENSION_KEY = 'extension'
INTENSION_KEY = 'intension'

import os
PATH_HERE = os.path.abspath(os.path.dirname(__file__))
PATH_REPO = os.path.dirname(PATH_HERE)
PATH_DATA = os.path.expanduser('~/geotaste_data')
PATH_ASSETS = os.path.join(PATH_HERE, 'assets')


# Urls
URLS=dict(
    books='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/1.3-beta/books.csv',
    members='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/1.3-beta/members.csv',
    events='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/1.3-beta/events.csv',
    dwellings='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/1.3-beta/dwellings.csv',
    creators='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/1.2/creators.csv',
    geojson_arrond='https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson?lang=en&timezone=Europe%2FParis'
)

# Paths
PATHS=dict(
    members = os.path.join(PATH_DATA,'members.csv'),
    books = os.path.join(PATH_DATA,'books.csv'),
    events = os.path.join(PATH_DATA,'events.csv'),
    dwellings = os.path.join(PATH_DATA,'dwellings.csv'),
    creators = os.path.join(PATH_DATA,'creators.csv'),
)

LATLON_SCO = (48.85107555543428, 2.3385039932538567)
MAP_CENTER = dict(lat=LATLON_SCO[0], lon=LATLON_SCO[1])
DISPREFERRED_ADDRESSES = {
    '11 rue Scribe': 'American Express',
    'Berkeley Street': 'Thomas Cook', # @CHECK
    '': 'Empty street address'
}
DWELLING_ID_SEP='; '











## Sys imports
from datetime import datetime as dt
import copy,time,sys,os
import random
import pandas as pd
import numbers

## Non-sys imports
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from functools import cached_property, lru_cache
cache = lru_cache(maxsize=None)
import dash
from dash import Dash, dcc, html, Input, Output, dash_table, callback, State, ctx
from dash.exceptions import PreventUpdate
from pprint import pprint, pformat
import dash_bootstrap_components as dbc
from dash_oop_components import DashApp, DashComponent, DashFigureFactory
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
# import pandas_dash
from pandas.api.types import is_numeric_dtype, is_string_dtype
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
import plotly.express as px
import plotly.graph_objects as go


## Setup plotly
# Plotly mapbox public token
try:
    mapbox_access_token = open(os.path.expanduser('~/.mapbox_token')).read()
    px.set_mapbox_access_token(mapbox_access_token)
except FileNotFoundError:
    pass

from .utils import *
from .datasets import *
from .widgets import *
from .figs import *
from .components import *
from .layout import *
from .app import *