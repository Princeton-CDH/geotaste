##################################################
# IMPORTS
##################################################

## Constants
TITLE = 'Geography of Taste'
TABLE_TEXT_COLOR='white'
COLORABLE_COLS = ['arrond_id', 'gender', 'is_expat', 'nation']

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
from dash import Dash, dcc, html, Input, Output, dash_table
import pandas_dash




##################################################
# UTILS
##################################################

def get_dropdown(
        options=[], 
        value=None,
        id=None,
        sort_alpha=False, 
        default=[], 
        input_type=dcc.Dropdown,
        **kwargs):
    if id is None and hasattr(series,'name'): id=series.name
    assert id is not None

    # get options
    if type(options) is pd.Series:
        opts = list(options.value_counts().index) if not sort_alpha else list(sorted(set(options)))
        opts = [str(x) for x in opts]
        options = [dict(label=x if x!='' else '(empty)', value=x) for x in opts]
    elif type(options) is list and options and type(options[0])!=dict:
        options = [dict(label=x, value=x) for x in options]

    drop = input_type(
        id=id,
        options=options,
        value=value if value is not None else default,
        **kwargs
    )
    return drop

def get_labeled_dropdown(*args, label='', **kwargs):
    dropdown = get_dropdown(*args, **kwargs)
    return get_labeled_element(dropdown, label)

def get_labeled_element(element, label=''):
    if not label:
        label = element.id.replace('_',' ').title() + ('?' if element.id.startswith('is_') else '')
    return dbc.Row([
        dbc.Col(html.Label(label), width=4),
        dbc.Col(element, width=8),
    ])

def get_labeled_slider(series, label='', step=10, id=None):
    s = pd.to_numeric(series, errors='coerce')
    slider = dcc.RangeSlider(
        id=id,
        min=s.min() // step * step,
        max=s.max() // step * step + step,
        step=step,
        marks=None,
        tooltip={"placement": "bottom", "always_visible": True}
    )
    return get_labeled_element(slider, label)

def get_labeled_checklist(*args, **kwargs):
    kwargs['input_type']=dcc.Checklist
    return get_labeled_dropdown(*args, **kwargs)




##################################################
# DATA
##################################################


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
def get_filtered_data_members(map_kind='all'): 
    map_kind=str(map_kind).lower()
    if 'all' in map_kind:
        return get_total_data_members()
    elif 'without' in map_kind:
        df1=get_total_data_members()
        df2=get_total_data_events()
        does_have_records = set(df2.member_id)
        return df1[~df1.member_id.isin(does_have_records)]
    else:
        return get_total_data_events()




##################################################
# COMPONENTS
##################################################


def DashMembersMap(
        dff = None, 
        color_choro='arrond_id', 
        color_points='is_expat',
        map_kind='all'):
    
    
    # if is_expat:
    #     dff = dff[dff.is_expat.apply(str).isin(is_expat)]
    
    # if gender:
    #     dff = dff[dff.gender.apply(str).isin(gender)]
        
    # if nation:
        # dff = dff[dff.nation.apply(lambda x: bool(set(x.split(';')) & set(nation)))]


    dff = get_filtered_data_members(map_kind) if dff is None else dff
    

    fig_choro = px.choropleth_mapbox(
        dff,
        geojson=get_geojson_arrondissement(),
        locations='arrond_id', 
        color=color_choro,
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
        color=color_points,
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
    
    return fig3



def DashMembersDataTable(dff = None, ocols = ['name','title','gender','birth_year','death_year','nationalities','street_address', 'start_date', 'end_date']):
    dff = get_filtered_data_members() if dff is None else dff

    ddt, ddt_cols = dff[ocols].dash.to_dash_table()
    return dash_table.DataTable(
        data=ddt,
        columns=ddt_cols,
        sort_action="native",
        sort_mode="multi",
        filter_action="native",
    )



##################################################
# LAYOUT
##################################################


layout = dbc.Container(
    dbc.Row([
        dbc.Col([
            html.H1(TITLE),
            html.P(children=[
                "The ",
                dcc.Link("Shakespeare & Co Project", href='https://shakespeareandco.princeton.edu/'),
                " uses the lending library records... Below are filters for the map to the right. Who borrowed what when where among expats in early 20th century Paris?"
            ]),

            html.Hr(),


            # get_labeled_dropdown(
            #     COLORABLE_COLS, 
            #     id='color_cols', 
            #     sort_alpha=True
            # ),

            get_labeled_checklist(
                [
                    'With borrowing records', 
                    'Without borrowing records'
                ], 
                id='map_kind',
                value=['With borrowing records'],
                label='Members',
                sort_alpha=True,
            ),

            get_labeled_checklist(
                get_members_df().gender,
                id='gender',
                label='Member gender',
            ),
            
            get_labeled_checklist(
                get_members_df().is_expat,
                id='is_expat',
                input_type=dcc.Checklist
            ),
            

            get_labeled_dropdown(
                pd.Series([nat for nations in get_members_df().nationalities for nat in nations.split(';')]),
                id='nation'
            ),

            get_labeled_slider(
                get_members_df().birth_year,
                id='birth_year'
            ),

            get_labeled_checklist(
                get_members_df().generation,
                id='generation'
            ),

            get_labeled_checklist(
                get_members_df().has_wikipedia,
                id='has_wikipedia',
                inline=True
            ),

            get_labeled_checklist(
                get_members_df().has_viaf,
                id='has_viaf',
                inline=True
            ),

            html.Hr(),


            


            # html.H2('Authors'),


            # html.H2('Books'),


            # html.Div(id='members-table', children=[DashMembersDataTable()])
            
        ], width=4, id='layout-col-left'),
    
    dbc.Col([
        
        
        # dbc.Row([
        dbc.Tabs([
            dbc.Tab([
                mapobj := dcc.Graph(id='members-map', figure=DashMembersMap(), className='div-for-charts')
            ], label='Map'),
            dbc.Tab([
                maptbl := html.Div(id='members-table', children=[DashMembersDataTable()])
            ], label='Table')
        ]),
    ], width=8, id='layout-col-right'),

]), id='layout-container')




dbc.Tabs()


#############
# APP SETUP #
#############

## Setup plotly
# Plotly mapbox public token
mapbox_access_token = open(os.path.expanduser('~/.mapbox_token')).read()
px.set_mapbox_access_token(mapbox_access_token)

# Setup app
app = Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title=TITLE,
)
server = app.server
app.layout = layout


@app.callback(
    [
        Output(mapobj, "figure"),
        Output(maptbl, 'children')
    ],
    [
        Input('map_kind', 'value'),
        # Input('dropdown-nation', 'value'),
        # Input('dropdown-gender', 'value'),
    ]
)
def update_map_and_table(map_kind):
    dff = get_filtered_data_members(map_kind)
    members = set(dff.member_id)
    df_tbl = get_total_data_members()
    df_tbl = df_tbl[df_tbl.member_id.isin(members)]

    return DashMembersMap(dff), DashMembersDataTable(df_tbl)

    

















# def DashTab(children=[], id='', label=''):
#     return dcc.Tab(
#         children,
#         id,
#         label,
#     )

# def DashMembersTab():
#     df = get_total_data_members()
    
#     # is_expat = dcc.RadioItems(
#     #     options=df.dash.to_options('is_expat'),
#     #     value='True',
#     #     id='radio-is_expat'
#     # )
#     is_expat = dcc.Dropdown(
#         options=['True','False'],
#         value=['True','False'],
#         id='dropdown-is_expat',
#         multi=True
#     )
    
#     all_nations = [k for k,v in Counter([nat for nations in df.nationalities for nat in nations.split(';')]).most_common()]
#     nations = dcc.Dropdown(
#         options=all_nations,
#         value=[],
#         id='dropdown-nation',
#         multi=True,
#     )

#     genders_l = list(df.gender.value_counts().index)
#     genders = dcc.Dropdown(
#         options=genders_l,
#         value=genders_l,
#         id='dropdown-gender',
#         multi=True,
#     )
    
    
    
#     return DashTab(
#         children=[
#             html.Label('The library member is an expat (i.e. not French).'),
#             is_expat,
            
#             html.Label('Nationality of member'), nations,

#             html.Label('Gender of member'), genders
            
#         ],
#         id='members_tab',
#         label='Filter members',
#     )

# def DashBooksTab():
#     df = get_books_df().fillna('')
#     authors = list(df['author'].value_counts().index)
    
#     content = [
#         dcc.Dropdown(
#             options=authors,
#             value='Woolf, Virginia',
#             id='dropdown-author'
#         )
#     ]
    
#     return DashTab(
#         content,
#         id='books_tab',
#         label='Books',
#     )

# def DashEventsTab():
#     return DashTab(
#         id='events_tab',
#         label='Events',
#     )


# def DashTabLayout():
#     return dcc.Tabs(
#             [
#                 DashMembersTab(),
#                 DashBooksTab(),
#                 DashEventsTab()
#             ]
#         )



    
# # Update Map Graph based on date-picker, selected data on histogram and location dropdown
# @app.callback(
#     [
#         Output("members-map", "figure"),
#         Output("members-table", "children"),
#     ],
#     [
#         Input('dropdown-is_expat', 'value'),
#         Input('dropdown-nation', 'value'),
#         Input('dropdown-gender', 'value'),
#     ]
# )
# def DashMembersMap(is_expat=None, nation=None, gender=None, color_by='arrond_id'):
#     dff = get_filtered_data_members().sample(frac=1)
    
#     if is_expat:
#         dff = dff[dff.is_expat.apply(str).isin(is_expat)]
    
#     if gender:
#         dff = dff[dff.gender.apply(str).isin(gender)]
        
#     if nation:
#         dff = dff[dff.nation.apply(lambda x: bool(set(x.split(';')) & set(nation)))]
        
#     fig_choro = px.choropleth_mapbox(
#         dff,
#         geojson=get_geojson_arrondissement(),
#         locations='arrond_id', 
#         color='arrond_id',
#         center=dict(lat=latlon_SCO[0], lon=latlon_SCO[1]),
#         zoom=12,
#         opacity=.1
#     )
#     # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        

#     fig = px.scatter_mapbox(
#         dff, 
#         lat="lat", 
#         lon="lon", 
#         center=dict(lat=latlon_SCO[0], lon=latlon_SCO[1]),
#         # hover_name="member_id", 
#         color='is_expat',
#         # hover_data=["State", "Population"],
#         # color_discrete_sequence=["fuchsia"], 
#         zoom=12, 
#         # size=10
#         # marker=dict(size=100),
#         # height=300
#     )
#     fig.update_layout(
#         mapbox=dict(
#             style="stamen-toner",
#         ),
#     )
#     fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
#     fig3 = go.Figure(data=fig.data + fig_choro.data, layout = fig.layout)
    
#     return fig3, DashMembersDataTable()







# def DashLeftLayout():
#     return dbc.Col(
#         children=[
#             html.H1(TITLE),
#             DashTabLayout()
#         ],
#         width=4,
#         id='layout-col-left'
#     )


# def DashMemberMapTab():
#     return dbc.Tab(
#         dbc.Row([
#             dcc.Graph(id='members-map'),
#             html.Div(id='members-table')
#         ]),
#         id='members_map_tab',
#         label='Map members'
#     )

# def DashEventsMapTab():
#     return dbc.Tab(
#         dcc.Graph(id='events-map'),
#         id='events_map_tab',
#         label='Map events'
#     ) 

# def DashRightLayout():
#     return dbc.Col(
#         dbc.Tabs([
#             DashMemberMapTab(),
#             DashEventsMapTab()
#         ]),
#         width=8,
#         id='layout-col-right'
#     )

# def DashLayout():
#     return dbc.Container([
#         dbc.Row([
#             DashLeftLayout(), 
#             DashRightLayout()
#         ], id='layout-container-row1'),
#     ], id='layout-container')
   

# #   





if __name__ == "__main__":
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


