###########
# IMPORTS #
###########

## Constants
TITLE = 'Geography of Taste'
TABLE_TEXT_COLOR='white'

## Sys imports
from datetime import datetime as dt
import os,sys,copy,time
heredir = os.path.abspath(os.path.dirname(__file__))
codedir = os.path.dirname(heredir)
sys.path.insert(0,codedir)
from geotaste import *

## Non-sys imports
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from flask_caching import Cache
import diskcache
from dash import Dash, dcc, html, Input, Output, DiskcacheManager, dash_table, State
import pandas_dash

#############
# APP SETUP #
#############

## Setup plotly

# Plotly mapbox public token
mapbox_access_token = open(os.path.expanduser('~/.mapbox_token')).read()
px.set_mapbox_access_token(mapbox_access_token)

## Setup dash

# # Setup callback cache
# callback_cache = diskcache.Cache(os.path.join(path_data,'callback.cache'))
# background_callback_manager = DiskcacheManager(callback_cache)

# Setup app
app = Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    # use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title=TITLE,
    # background_callback_manager=background_callback_manager
)
server = app.server # set aside for gunicorn

# # # Setup data cache
# CACHE_CONFIG = {
#     'CACHE_TYPE': 'FileSystemCache',
#     'CACHE_IGNORE_ERRORS': True,
#     'CACHE_DIR':os.path.join(path_data,'app_cache')
# }
# cache = Cache()
# cache.init_app(app.server, config=CACHE_CONFIG)



########
# DATA #
########


@cache
def get_total_data_members():
    print('getting total_data_members')
    return filter_figdf(get_members_df(with_dwellings=True))

@cache
def get_total_data_events():
    # df = get_combined_filtered_events_from_choices()
    print('getting total_data_events')
    df = pd.read_pickle(os.path.join(heredir,'data.pkl'))
    return filter_figdf(df).merge(get_members_df(), on='member_id')


## Filtering

def get_filtered_data_members(): return get_total_data_members()




# #@TODO: datatable




##########
# LAYOUT #
##########



def DashMembersDataTable(df=None):
    df = get_total_data_members() if df is None else df
    ocols = ['name','title','gender','birth_year','death_year','nationalities','street_address', 'start_date', 'end_date']
    ddt, ddt_cols = df[ocols].dash.to_dash_table(
        # column_properties={"country": {"presentation": "markdown"}}
    )
    return dash_table.DataTable(
        data=ddt,
        columns=ddt_cols,
        sort_action="native",
        sort_mode="multi",
        filter_action="native",
        merge_duplicate_headers=True,
        # virtualization=True,
        # style_cell={'color':TABLE_TEXT_COLOR},
        # style_table={'height':300},
        # style_as_list_view=True,
        # style_data_conditional=[
        #     {
        #         'if': {'row_index': 'odd'},
        #         'backgroundColor': 'rgba(255, 255, 255, .1)',
        #     }
        # ],
        
    )



def DashTab(children=[], id='', label=''):
    return dcc.Tab(
        children,
        id,
        label,
    )

def DashMembersTab():
    df = get_total_data_members()
    
    # is_expat = dcc.RadioItems(
    #     options=df.dash.to_options('is_expat'),
    #     value='True',
    #     id='radio-is_expat'
    # )
    is_expat = dcc.Dropdown(
        options=['True','False'],
        value=['True','False'],
        id='dropdown-is_expat',
        multi=True
    )
    
    all_nations = [k for k,v in Counter([nat for nations in df.nationalities for nat in nations.split(';')]).most_common()]
    nations = dcc.Dropdown(
        options=all_nations,
        value=[],
        id='dropdown-nation',
        multi=True,
    )

    genders_l = list(df.gender.value_counts().index)
    genders = dcc.Dropdown(
        options=genders_l,
        value=genders_l,
        id='dropdown-gender',
        multi=True,
    )
    
    
    
    return DashTab(
        children=[
            html.Label('The library member is an expat (i.e. not French).'),
            is_expat,
            
            html.Label('Nationality of member'), nations,

            html.Label('Gender of member'), genders
            
        ],
        id='members_tab',
        label='Members',
    )

def DashBooksTab():
    df = get_books_df().fillna('')
    authors = list(df['author'].value_counts().index)
    
    content = [
        dcc.Dropdown(
            options=authors,
            value='Woolf, Virginia',
            id='dropdown-author'
        )
    ]
    
    return DashTab(
        content,
        id='books_tab',
        label='Books',
    )

def DashEventsTab():
    return DashTab(
        id='events_tab',
        label='Events',
    )


def DashTabLayout():
    return dcc.Tabs(
            [
                DashMembersTab(),
                DashBooksTab(),
                DashEventsTab()
            ]
        )



    
# Update Map Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    [
        Output("members-map", "figure"),
        Output("members-table", "children"),
    ],
    [
        Input('dropdown-is_expat', 'value'),
        Input('dropdown-nation', 'value'),
        Input('dropdown-gender', 'value'),
    ]
)
def DashMembersMap(is_expat=None, nation=None, gender=None, color_by='arrond_id'):
    dff = get_filtered_data_members().sample(frac=1)
    
    if is_expat:
        dff = dff[dff.is_expat.apply(str).isin(is_expat)]
    
    if gender:
        dff = dff[dff.gender.apply(str).isin(gender)]
        
    if nation:
        dff = dff[dff.nation.apply(lambda x: bool(set(x.split(';')) & set(nation)))]
        
    fig_choro = px.choropleth_mapbox(
        dff,
        geojson=get_geojson_arrondissement(),
        locations='arrond_id', 
        color='arrond_id',
        center=dict(lat=latlon_SCO[0], lon=latlon_SCO[1]),
        zoom=12,
        opacity=.1
    )
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        

    fig = px.scatter_mapbox(
        dff, 
        lat="lat", 
        lon="lon", 
        center=dict(lat=latlon_SCO[0], lon=latlon_SCO[1]),
        # hover_name="member_id", 
        color='is_expat',
        # hover_data=["State", "Population"],
        # color_discrete_sequence=["fuchsia"], 
        zoom=12, 
        # size=10
        # marker=dict(size=100),
        # height=300
    )
    fig.update_layout(
        mapbox=dict(
            style="stamen-toner",
        ),
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    fig3 = go.Figure(data=fig.data + fig_choro.data, layout = fig.layout)
    
    return fig3, DashMembersDataTable()



def DashOffLayout():
    return html.Div([
        dbc.Offcanvas(
            DashLeftLayout(),
            id="offcanvas",
            title="Title????",
            is_open=False,
        )
    ])























@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

def DashLeftLayout():
    return dbc.Col(
        children=[
            html.H1(TITLE),
            DashTabLayout()
        ],
        width=4,
        id='layout-col-left'
    )


def DashMemberMapTab():
    return dbc.Tab(
        dbc.Row([
            dcc.Graph(id='members-map'),
            html.Div(id='members-table')
        ]),
        id='members_map_tab',
        label='Map members'
    )

def DashEventsMapTab():
    return dbc.Tab(
        dcc.Graph(id='events-map'),
        id='events_map_tab',
        label='Map events'
    ) 

def DashRightLayout():
    return dbc.Col(
        dbc.Tabs([
            DashMemberMapTab(),
            DashEventsMapTab()
        ]),
        width=8,
        id='layout-col-right'
    )

def DashLayout():
    return dbc.Container([
        dbc.Row([
            dbc.Col('Hello'),
            dbc.Col([
                dbc.Button("Open Offcanvas", id="open-offcanvas", n_clicks=0)
            ],
            style={'text-align':'right'}
            )
        ]),
        dbc.Row([
            DashRightLayout()
        ], id='layout-container-row1'),
    ], id='layout-container')
   

#   

app.layout = DashLayout()

if __name__ == "__main__":
    app.run(
        # host='0.0.0.0', 
        debug=True,
        port=8052,
        # threaded=True,
        # dev_tools_ui=Fas,
        use_reloader=True,
        use_debugger=True,
        reloader_interval=1,
        reloader_type='watchdog'
    )