
## Constants
TITLE = 'Geography of Taste'
TABLE_TEXT_COLOR='white'
COLORABLE_COLS = ['arrond_id', 'gender', 'is_expat', 'nation']

## Import geotaste
import os,sys
heredir = os.path.abspath(os.path.dirname(__file__))
codedir = os.path.dirname(heredir)
sys.path.insert(0,codedir)
sys.path.insert(0,heredir)
from geotaste import *

## Import app imports
from datetime import datetime as dt
import copy,time

## Non-sys imports
import dash
# import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table, callback
import pandas_dash


# internal
from app_data import *
from app_figs import *
from app_widgets import *
from app_layout import *
from app_callbacks import *