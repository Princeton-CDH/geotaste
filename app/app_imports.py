## Constants
LEFT_COLOR='#7d6ab6'
RIGHT_COLOR='#1a6b47'
BOTH_COLOR='#354469'

EXTENSION_KEY = 'extension'
INTENSION_KEY = 'intension'


## Sys imports
from datetime import datetime as dt
import copy,time,sys,os
import random
import pandas as pd
import numbers

## Non-sys imports
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
mapbox_access_token = open(os.path.expanduser('~/.mapbox_token')).read()
px.set_mapbox_access_token(mapbox_access_token)

# geotaste imports
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from geotaste import *





# local imports
from app_utils import *
from app_widgets import *
from app_figs import *
from app_components import *
from app_layout import *