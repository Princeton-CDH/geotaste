# import dash
# from dash import html, dcc, callback, Input, Output

# dash.register_page(__name__)

# layout = html.Div([
#     html.H1('Testing')
# ])


# import geotaste
import sys; sys.path.insert(0,'..')
from geotaste import *

TITLE = 'GeoTaste: Shakespeare & Co Lab'


import dash
from dash import dcc
from dash import html
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
)
app.title = TITLE
server = app.server

# Plotly mapbox public token
mapbox_access_token = open(os.path.expanduser('~/.mapbox_token')).read()
px.set_mapbox_access_token(mapbox_access_token)

# get data
# df = filter_figdf(get_combined_filtered_events_for())
# df = pd.read_pickle('data.pkl')
# df = df[df.arrond_id!='']
# df.to_pickle('data.pkl')



# Layout of Dash App
app.layout = html.Div(
    children=[
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.H2(TITLE),
                        html.P(
                            """Select different days using the date picker or by selecting
                            different time frames on the histogram."""
                        ),


                        # html.Div(
                        #     className="div-for-dropdown",
                        #     children=[
                        #         # Dropdown for locations on map
                        #         dcc.Dropdown(
                        #             id="book-dropdown",
                        #             options=[
                        #                 {"label": i, "value": i}
                        #                 for i in df.book_id
                        #             ],
                        #             placeholder="Select a book",
                        #             value='joyce-ulysses'
                        #         )
                        #     ],
                        # ),

                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                # Dropdown for locations on map
                                dcc.Dropdown(
                                    id="arrond-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in sorted(list(get_all_arrond_ids()),key=lambda x: int(x))
                                    ],
                                    placeholder="Select arrondissement",
                                    value='6'
                                )
                            ],
                        ),

                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                # Dropdown for locations on map
                                dcc.Dropdown(
                                    id="color-by-dropdown",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in ['is_expat', 'gender']
                                    ],
                                    placeholder="Select something to color by",
                                    value='is_expat'
                                )
                            ],
                        ),

                        dcc.Graph(id="map-graph3"),
                    ],

                    


                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="map-graph"),
                        dcc.Graph(id="map-graph2"),
                        
                    ],
                ),
            ],
        )
    ]
)

# Update Map Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    Output("map-graph3", "figure"),
    [
        Input('color-by-dropdown', 'value'),
        Input('arrond-dropdown', 'value'),
    ]
)
def update_members_chart(color_by, arrond_id):
    dff = filter_figdf(
        get_dwellings_df()
    ).merge(get_members_df(), on='member_id').query(
        f'arrond_id == "{arrond_id}"'
    )

    color_by='gender'
    data = dff.groupby(['nation', color_by]).count().member_id.reset_index().rename({'member_id':'count'},axis=1)
    fig = px.bar(
        data, 
        y='nation', 
        x='count',
        color=color_by,
        color_discrete_sequence=px.colors.colorbrewer.Dark2
    )

    return fig


@app.callback(
    Output("map-graph", "figure"),
    [
        Input('color-by-dropdown', 'value'),
        Input('arrond-dropdown', 'value'),
    ]
)
def update_members_graph(color_by, arrond_id):
    zoom = 12.0
    bearing = 0

    dff = filter_figdf(get_dwellings_df()).merge(get_members_df(), on='member_id')
    dff['order_num'] = list(range(len(dff)))
    dff['order_num']+= 1
    dff['order_str'] = dff['order_num'].apply(str)

    print(list(dff.columns))

    fig = px.scatter_mapbox(
        dff, 
        lat="lat", 
        lon="lon", 
        center=dict(lat=latlon_SCO[0], lon=latlon_SCO[1]),
        # hover_name="member_id", 
        color=color_by,
        # hover_data=["State", "Population"],
        # color_discrete_sequence=["fuchsia"], 
        zoom=12, 
        # height=300
    )
    fig.update_layout(
        mapbox=dict(
            style="stamen-toner",
        ),
        height=500
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig


# Update Map Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    Output("map-graph2", "figure"),
    [
        Input('color-by-dropdown', 'value'),
        Input('arrond-dropdown', 'value'),
    ]
)
def update_events_graph(color_by, arrond_id):
    zoom = 12.0
    bearing = 0

    df = pd.read_pickle('data.pkl')
    df = df[df.arrond_id!='']

    dff = filter_figdf(df).merge(get_members_df(), on='member_id')

    fig = px.scatter_mapbox(
        dff, 
        lat="lat", 
        lon="lon", 
        center=dict(lat=latlon_SCO[0], lon=latlon_SCO[1]),
        # hover_name="member_id", 
        color=color_by,
        # hover_data=["State", "Population"],
        # color_discrete_sequence=["fuchsia"], 
        zoom=12, 
        # height=300
    )
    fig.update_layout(
        mapbox=dict(
            style="stamen-toner",
        ),
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig


if __name__ == "__main__":
    app.run_server(debug=True, port=8052,  threaded=True)