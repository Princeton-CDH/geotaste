## Sys imports
from datetime import datetime as dt
import copy,time,sys,os

## Non-sys imports
import dash
from dash import Dash, dcc, html, Input, Output, dash_table, callback, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import pandas_dash

# geotaste imports
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
from geotaste import *


## Start app

app = Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    title='Geography of Taste',
)
server = app.server



## Set layout



search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.Button(
                "Search", color="primary", className="ms-2", n_clicks=0
            ),
            width="auto",
        ),
    ],
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

# tabs_bar = dbc.Tabs([
#         dbc.Tab(label="Members", tab_id="members"),
#         dbc.Tab(label="Books", tab_id="books"),
#         dbc.Tab(label="Borrows", tab_id="borrows"),
#     ],
#     id="tabs",
#     active_tab="members",
#     class_name='tabs',
# )

tabs_bar = dcc.Tabs([
        dcc.Tab(label="Members", value="members"),
        dcc.Tab(label="Books", value="books"),
        dcc.Tab(label="Borrows", value="borrows"),
    ],
    className='tabs',
    value='members'
)

tabs_row = dbc.Row(
     tabs_bar, 
)


navbar = dbc.Navbar(
    dbc.Container([
        # Use row and col to control vertical alignment of logo / brand
        dbc.Row(
            [
                dbc.Col(
                    html.Img(src="/assets/SCo_logo_graphic.png", height="30px")
                ),
                dbc.Col(
                    dbc.NavbarBrand(
                        "Geography of Taste", 
                    ),
                ),
            ],
            align="center",
            style={'margin':'auto'},
        ),
    ]),
    color="light",
    dark=False,
)


def sidecol(tabname='members', **kwargs):
    return globals()[f'sidecol_{tabname}']


"""
Text filter by name (type in name of member) and find out where they live.
Compare by gender
Compare by birth date
Membership date
Nationality
Arrondissement 
Ability to select multiple options
"""

sidecol_members = dbc.Col([
    html.H2('Members'),

    ## member search
    dbc.Input(type='search', list='member-datalist', placeholder='Select a member'),
    html.Datalist(
        id='member-datalist', 
        children=[
            html.Option(value=x, label=y)
            for x,y in zip(Members().data.index, Members().data.name)
        ]
    ),
], width=3)




def sidecol_content_books(**kwargs):
    return [
        html.H2('Books'),

    ]

def sidecol_content_borrows(**kwargs):
    return [
        html.H2('Borrows'),
    ]




maincol = dbc.Col(
    width=9,
    children=[
        map_div := dcc.Graph(),
        data_tbl := dbc.Container(children=[Members().data_table()])
    ]
)


app.layout = layout_container = dbc.Container([
    navbar_row := dbc.Row(navbar),
    tabs_row,
    content_row := dbc.Row()
])



## callbacks
@callback(
    Output(content_row, 'children'),
    Input(tabs_bar, 'value')
)
def go(active_tab):
    print(active_tab)
    return dbc.Row([
        sidecol(active_tab),
        maincol
    ])


# # add callback for toggling the collapse on small screens
# @callback(
#     Output("navbar-collapse", "is_open"),
#     [Input("navbar-toggler", "n_clicks")],
#     [State("navbar-collapse", "is_open")],
# )
# def toggle_navbar_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open









if __name__=='__main__':
    app.run(
        host='0.0.0.0', 
        debug=True,
        port=8052,
        # threaded=True,
        # dev_tools_ui=Fas,
        use_reloader=True,
        use_debugger=True,
        reloader_interval=1,
        reloader_type='watchdog'
    )

