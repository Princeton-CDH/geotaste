## Constants

# server
PORT=8111
HOST='0.0.0.0'
DEBUG=True

LOG_FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{message}</level> | <cyan>{function}</cyan> | <cyan>{file}</cyan>:<cyan>{line}</cyan>'


# 5 to include traces; 
# 10 for debug; 20 info, 25 success; 
# 30 warning, 40 error, 50 critical;
LOG_LEVEL = 10

    

# stats
MIN_P=.05

# blanks etc
BLANKSTR='‎‎‎‎'
BLANK = ''
UNFILTERED = 'Add filter'
UNFILTERED_L = 'Filter 1'
UNFILTERED_R = '+'

NOFILTER = BLANK
# LEFT_COLOR='#AB9155' #'#7d6ab6'
RIGHT_COLOR='#7d6ab6' #rgb(125, 106, 182)
LEFT_COLOR='#40b0a6' #rgb(64, 176, 166)'
BOTH_COLOR='#606060'
DEFAULT_COLOR=LEFT_COLOR
PLOTLY_TEMPLATE='simple_white'
UNKNOWN='(Unknown)'
STYLE_INVIS={'display':'none'}
STYLE_VIS={'display':'flex'}
LOGO_SRC="/assets/SCo_logo_graphic-small.png"
LOGO_SRC2="/assets/rulerlab-small.png"

# paths
import os
PATH_HERE = os.path.abspath(os.path.dirname(__file__))
PATH_REPO = os.path.dirname(PATH_HERE)
PATH_DATA = os.path.expanduser('~/geotaste_data')
PATH_ASSETS = os.path.join(PATH_HERE, 'assets')

# Urls
URLS=dict(
    books='https://raw.githubusercontent.com/Princeton-CDH/geotaste/newdataset/data/1.3-beta/books-with-genres.csv',
    members='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/1.3-beta/members.csv',
    events='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/1.3-beta/events.csv',
    landmarks='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/landmarks.csv',
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
    combined = os.path.join(PATH_DATA,'combined.pkl.gz'),
    landmarks = os.path.join(PATH_DATA,'landmarks.csv'),
)

LATLON_SCO = (
    48.85107555543428, 
    2.3385039932538567
)

CENTER = (
    # LATLON_SCO[0] + .005,
    # LATLON_SCO[1] - .015

    LATLON_SCO[0],
    LATLON_SCO[1]
)

MAP_CENTER = dict(
    lat=CENTER[0],
    lon=CENTER[1]
)
MAP_CENTER_SCO = dict(
    lat=LATLON_SCO[0],
    lon=LATLON_SCO[1]
)
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
from numbers import Number
import json
from collections import Counter

# for typing purposes
from typing import *
from collections.abc import *

## Non-sys imports
import orjson
from sqlitedict import SqliteDict
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import warnings
warnings.filterwarnings('ignore')
from functools import cached_property, cache
# cache = lru_cache(maxsize=None)
from diskcache import Cache
cache_obj = Cache(os.path.join(PATH_DATA, 'cache.dc'))
# cache = cache_obj.memoize()
import dash
from dash import Dash, dcc, html, Input, Output, dash_table, callback, State, ctx, ClientsideFunction, MATCH, ALL
BLANKDIV = html.Div(BLANKSTR)
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
import plotly.express as px
import plotly.graph_objects as go
from humanfriendly import format_timespan

# setup logs
from loguru import logger
logger.remove()
logger.add(
    sink = sys.stderr,
    format=LOG_FORMAT, 
    level=LOG_LEVEL
)

## Setup plotly
# Plotly mapbox public token
try:
    mapbox_access_token = open(os.path.expanduser('~/.mapbox_token')).read()
    px.set_mapbox_access_token(mapbox_access_token)
except FileNotFoundError:
    mapbox_access_token = None

from .utils import *
from .queries import *
from .statutils import *
from .queries import *
from .statutils import *
from .datasets import *
from .figs import *
from .components import *
from .panels import *
from .layouts import *
from .app import *
from .figs import *
from .components import *
from .panels import *
from .layouts import *
from .app import *