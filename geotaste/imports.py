## Constants
MIN_P=.1
LEFT_COLOR='#AB9155' #'#7d6ab6'
RIGHT_COLOR='#40B0A6' ##bf6927'
BOTH_COLOR='#606060'
PLOTLY_TEMPLATE='simple_white'
UNKNOWN='(Unknown)'

# LEFT_COLOR='#d2afff'
# RIGHT_COLOR='#FF007F'

STYLE_INVIS={'display':'none'}
STYLE_VIS={'display':'flex'}

# STYLE_INVIS={'visibility':'hidden'}
# STYLE_VIS={'visibility':'visible'}

# STYLE_INVIS = {'position': 'absolute', 'top': '-9999px', 'left': '-9999px'}
# STYLE_VIS = {'position': 'relative'}

LOGO_SRC="/assets/SCo_logo_graphic-small.png"

EXTENSION_KEY = 'extension'
INTENSION_KEY = 'intension'

import os
PATH_HERE = os.path.abspath(os.path.dirname(__file__))
PATH_REPO = os.path.dirname(PATH_HERE)
PATH_DATA = os.path.expanduser('~/geotaste_data')
PATH_ASSETS = os.path.join(PATH_HERE, 'app', 'assets')


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
import json
from collections import Counter

## Non-sys imports
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import warnings
warnings.filterwarnings('ignore')
from functools import cached_property, lru_cache
cache = lru_cache(maxsize=None)
import dash
from dash import Dash, dcc, html, Input, Output, dash_table, callback, State, ctx, ClientsideFunction, MATCH, ALL
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
from .statutils import *
from .datasets import *
from .arronds import *
from .app import *
from .members import *
from .books import *
from .events import *
from .combined import *
from .comparison import *