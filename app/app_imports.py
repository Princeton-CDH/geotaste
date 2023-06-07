## Sys imports
from datetime import datetime as dt
import copy,time,sys,os

## Non-sys imports
import dash
from dash import Dash, dcc, html, Input, Output, dash_table, callback, State
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

from app_utils import *

## Setup plotly
# Plotly mapbox public token
mapbox_access_token = open(os.path.expanduser('~/.mapbox_token')).read()
px.set_mapbox_access_token(mapbox_access_token)




# geotaste imports
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from geotaste import *

