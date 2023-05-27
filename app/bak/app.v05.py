# import geotaste
import sys; sys.path.insert(0,'..')
from geotaste import *
TITLE = 'GeoTaste: Shakespeare & Co Lab'

import dash
import dash_bootstrap_components as dbc

from dash import dcc, html
import pandas as pd
import numpy as np
import plotly.express as px
from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt


app = dash.Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    # use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = TITLE
server = app.server

# Plotly mapbox public token
mapbox_access_token = open(os.path.expanduser('~/.mapbox_token')).read()
px.set_mapbox_access_token(mapbox_access_token)

def get_map_data_members():
    return filter_figdf(get_members_df(with_dwellings=True))


#@TODO: datatable

def get_layout_members_map():
    return html.H1('Hello world!')


def get_layout():
    return dcc.Tabs([
        dcc.Tab(
            get_layout_members_map(),
            'hello',
            'Hello'
        )
    ])

app.layout = get_layout()

if __name__ == "__main__":
    app.run_server(debug=True, port=8052,  threaded=True)