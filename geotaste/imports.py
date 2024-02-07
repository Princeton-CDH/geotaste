import os, tempfile, sys

# paths
PATH_HERE = os.path.abspath(os.path.dirname(__file__))
PATH_REPO = os.path.dirname(PATH_HERE)
PATH_DATA = os.path.expanduser('~/geotaste_data')
PATH_ASSETS = os.path.join(PATH_HERE, 'assets')
PATH_SRVR = os.path.join(PATH_DATA, 'webview.db')
PATH_LOG = os.path.join(PATH_DATA, 'geotaste.log')

USE_CACHE = False

# setup logs
LOG_FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <cyan>{function}</cyan> | <level>{message}</level> | <cyan>{file}</cyan>:<cyan>{line}</cyan>'

# 5 to include traces;
# 10 for debug; 20 info, 25 success;
# 30 warning, 40 error, 50 critical;
LOG_LEVEL = 10

from loguru import logger

logger.remove()
logger.add(sink=sys.stderr, format=LOG_FORMAT, level=LOG_LEVEL)
logger.add(sink=open(PATH_LOG, 'a'), format=LOG_FORMAT, level=LOG_LEVEL)


if not USE_CACHE:
    PATH_CACHE = tempfile.TemporaryDirectory().name
else:
    PATH_CACHE = os.path.join(PATH_DATA, 'cache.dc')

logger.debug({k: v for k, v in locals().items() if k.startswith('PATH_')})

## IMPORTS

## Sys imports
from datetime import datetime as dt
import copy, time, sys, os
import random
import pandas as pd
import numbers
from numbers import Number
import json, pickle
from collections import Counter

# for typing purposes
from typing import *
from collections.abc import *

## Non-sys imports
os.environ['ASSETS_FOLDER'] = PATH_ASSETS


import orjson
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'
import warnings

warnings.filterwarnings('ignore')
from functools import cached_property, cache

# cache = lru_cache(maxsize=None)

from diskcache import Cache

cache_obj = Cache(PATH_CACHE)
# cache = cache_obj.memoize()
import dash
from dash import (
    Dash,
    dcc,
    html,
    Input,
    Output,
    dash_table,
    callback,
    State,
    ctx,
    ClientsideFunction,
    MATCH,
    ALL,
    DiskcacheManager,
    Patch,
)

# background_manager = DiskcacheManager(cache_obj)
from dash.exceptions import PreventUpdate
from pprint import pprint, pformat
import dash_bootstrap_components as dbc
from dash_oop_components import DashApp, DashComponent, DashFigureFactory
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd

# import pandas_dash
from pandas.api.types import is_numeric_dtype, is_string_dtype
import plotly.express as px
import plotly.graph_objects as go
from humanfriendly import format_timespan
import zlib
from base64 import b64decode, b64encode
from colour import Color
import dash_leaflet as dl


MAPBOX_ACCESS_TOKEN_b64 = b'cGsuZXlKMUlqb2ljbmxoYm1obGRYTmxjaUlzSW1FaU9pSmpiRzFuYmpGM2NtNHdZV2Q1TTNKelpXOXVibXB3YzJwbEluMC5PQ0ZBVlppa0JHREZTOVRlQ0F6aDB3'
mapbox_access_token = b64decode(MAPBOX_ACCESS_TOKEN_b64).decode('utf-8')
px.set_mapbox_access_token(mapbox_access_token)
SEARCH_PARAM_PREFIX = '?'


#### CONSTANTS ########################################


BASEMAP_SOURCES = [
    'https://warper.wmflabs.org/maps/tile/6050/{z}/{x}/{y}.png',
    'https://shakespeareandco.app/tiles/data/paris1937/{z}/{x}/{y}.png',
]

# Paths
PATHS = dict(
    members=os.path.join(PATH_DATA, 'members.csv'),
    books=os.path.join(PATH_DATA, 'books.csv'),
    events=os.path.join(PATH_DATA, 'events.csv'),
    dwellings=os.path.join(PATH_DATA, 'dwellings.csv'),
    creators=os.path.join(PATH_DATA, 'creators.csv'),
    combined=os.path.join(PATH_DATA, 'combined.pkl.gz'),
    combinedmini=os.path.join(PATH_DATA, 'combined.mini.pkl.gz'),
    landmarks=os.path.join(PATH_DATA, 'landmarks.csv'),
)


# server
PORT = 1919
HOST = '0.0.0.0'
DEBUG = False
TEXTFONT_SIZE = 20
COMPARISON_MAXCATS = None

PREDICT_COLS = [
    'member_gender',
    'member_nationalities',
    'author',
    'author_gender',
    'author_nationalities',
    'book',
    'book_format',
    'book_genre',
    'arrond_id',
]
PREDICT_MIN_COUNT = 2
PREDICT_MIN_SUM = 10

WELOME_MSG_ON = True

DONOTCITE = 'Pre-release version: do not cite. Feedback: shakespeareandco@princeton.edu'
WELCOME_HEADER = 'Shakespeare and Company Project Lab'
WELCOME_HEADER2 = 'Experiment 1: Geography and Taste'
WELCOME_BODY = """Use the filters to generate and compare maps showing where members of the Shakespeare and Company lending library lived and the books they borrowed."""
SITE_TITLE = 'Shakespeare and Company Project Lab'
# stats
MIN_P = 0.05

# blanks etc
BLANKSTR = '‎‎‎‎'
BLANKDIV = html.Div(BLANKSTR)
BLANK = ''
UNFILTERED = 'Filter 1'
UNFILTERED_L = 'Filter 1'
UNFILTERED_R = 'Filter 2'

NOFILTER = BLANK
RIGHT_COLOR = '#7d6ab6'   # rgb(125, 106, 182)
LEFT_COLOR = '#40b0a6'   # rgb(64, 176, 166)'
BOTH_COLOR = '#606060'
DEFAULT_COLOR = LEFT_COLOR
PLOTLY_TEMPLATE = 'simple_white'
UNKNOWN = '(Unknown)'
STYLE_INVIS = {'display': 'none'}
STYLE_HALFVIS = {'opacity': 0.5, 'display': 'block'}
STYLE_VIS = {'display': 'block', 'opacity': 1}

ROOT_URL = ''


# Urls
URLS = dict(
    books='https://raw.githubusercontent.com/Princeton-CDH/geotaste/develop/data/1.3-beta/books-with-genres.csv',
    members='https://raw.githubusercontent.com/Princeton-CDH/geotaste/develop/data/1.3-beta/members.csv',
    events='https://raw.githubusercontent.com/Princeton-CDH/geotaste/develop/data/1.3-beta/events.csv',
    landmarks='https://raw.githubusercontent.com/Princeton-CDH/geotaste/develop/data/landmarks.csv',
    dwellings='https://raw.githubusercontent.com/Princeton-CDH/geotaste/develop/data/1.3-beta/dwellings.csv',
    creators='https://raw.githubusercontent.com/Princeton-CDH/geotaste/develop/data/1.3-beta/creators.csv',
    combinedmini='https://raw.githubusercontent.com/Princeton-CDH/geotaste/develop/data/1.3-beta/combined.mini.pkl.gz',
    geojson_arrond='https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson?lang=en&timezone=Europe%2FParis',
)

COMPARISON_SCALES = {
    # 'book': ['member','book'],  #'book'],
    # 'author': ['member','author'],  # ['author','event'],
    'member': ['member'],
    'arrond': ['member', 'arrond_id'],
    # 'book': ['book'],  #'book'],
    # 'author': ['author'],  # ['author','event'],
    # 'member': ['member'],
    # 'arrond': ['member', 'arrond_id'],
    'event': ['event'],
    'book': ['event'],
    'author': ['event'],
}


LATLON_SCO = (48.85107555543428, 2.3385039932538567)

CENTER = (
    # LATLON_SCO[0] + .005,
    # LATLON_SCO[1] - .015
    LATLON_SCO[0],
    LATLON_SCO[1],
)

MAP_CENTER = dict(lat=CENTER[0], lon=CENTER[1])
MAP_CENTER_SCO = dict(lat=LATLON_SCO[0], lon=LATLON_SCO[1])
DISPREFERRED_ADDRESSES = {
    '11 rue Scribe': 'American Express',
    'Berkeley Street': 'Thomas Cook',  # @CHECK
    '': 'Empty street address',
}
DWELLING_ID_SEP = '; '
TCOLS = [
    'event',
    'dwelling',
    'event_start',
    'event_end',
    'dwelling_start',
    'dwelling_end',
]


DEFAULT_STATE = {
    'bearing': 0,
    'lat': MAP_CENTER['lat'],
    'lon': MAP_CENTER['lon'],
    'pitch': 0,
    'zoom': 14,
    'tab': 'map',
    'tab2': 'arrond',
}


TEST_HOSTS = [f'http://127.0.0.1:5805{x}/' for x in range(10)]


#######################################################
## CONFIG OVERWRITES
import shutil, json

PATH_CONFIG_DEFAULT = os.path.join(PATH_REPO, 'config_default.json')
PATH_CONFIG = os.path.join(PATH_DATA, 'config.json')


def read_config_json(fn):
    if not os.path.exists(fn):
        return {}
    try:
        with open(fn) as f:
            return json.load(f)
    except Exception as e:
        logger.exception(e)
        return {}


# read
CONFIG = {
    **read_config_json(PATH_CONFIG_DEFAULT),
    **read_config_json(PATH_CONFIG),
}

# copy to globals
for ck, cv in CONFIG.items():
    globals()[ck] = cv

# ensure exists? -- empty?
if not os.path.exists(PATH_DATA):
    os.makedirs(PATH_DATA)
if not os.path.exists(PATH_CONFIG):
    with open(PATH_CONFIG, 'w') as of:
        json.dump({}, of)
#######################################################

if ROOT_URL.endswith('/'):
    ROOT_URL = ROOT_URL[:-1]
ASSETS_URL = f'{ROOT_URL}/assets'
LOGO_SRC = f'{ASSETS_URL}/SCo_logo_graphic-small.png'
LOGO_SRC2 = f'{ASSETS_URL}/rulerlab-small.png'
PATH_LOGO = os.path.join(PATH_ASSETS, os.path.basename(LOGO_SRC))


from .utils import *
from .querystrings import *
from .queries import *
from .statutils import *
from .datasets import *
from .figs import *
from .components import *
from .panels import *
from .layouts import *
from .app import *

# any preprocess steps
store_all_markers_in_assets_folder()
