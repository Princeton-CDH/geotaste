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
df = pd.read_pickle('data.pkl')
df = df[df.arrond_id!='']
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
                    ],

                    


                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(id="map-graph"),
                        
                    ],
                ),
            ],
        )
    ]
)

# Update Map Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    Output("map-graph", "figure"),
    [
        Input('color-by-dropdown', 'value')
        # Input("date-picker", "date"),
        # Input("bar-selector", "value"),
        # Input("location-dropdown", "value"),
    ],
)
def update_members_graph(color_by):
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
            style="satellite",
        ),
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig

# # Update Map Graph based on date-picker, selected data on histogram and location dropdown
# @app.callback(
#     Output("map-graph", "figure"),
#     [
#         Input('book-dropdown', 'value')
#         # Input("date-picker", "date"),
#         # Input("bar-selector", "value"),
#         # Input("location-dropdown", "value"),
#     ],
# )
# def update_graph(book):
#     zoom = 12.0
#     bearing = 0

#     dff = df[df.book_id == book] if book else df
#     dff['order_num'] = list(range(len(dff)))
#     dff['order_num']+= 1
#     dff['order_str'] = dff['order_num'].apply(str)

#     print(list(dff.columns))

#     fig = px.scatter_mapbox(
#         dff, 
#         lat="lat", 
#         lon="lon", 
#         center=dict(lat=latlon_SCO[0], lon=latlon_SCO[1]),
#         # hover_name="member_id", 
#         color='gender',
#         # hover_data=["State", "Population"],
#         # color_discrete_sequence=["fuchsia"], 
#         zoom=12, 
#         # height=300
#     )
#     fig.update_layout(
#         mapbox=dict(
#             style="satellite",
#         ),
#         height=600,
#         width=900
#     )
#     fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

#     fig

#     return fig
    
#     return go.Figure(
#         data=[
#             fig,
            
#         ],
#         layout=Layout(
#             autosize=True,
#             margin=go.layout.Margin(l=0, r=35, t=0, b=0),
#             showlegend=False,
#             mapbox=dict(
#                 accesstoken=mapbox_access_token,
#                 center=dict(lat=latlon_SCO[0], lon=latlon_SCO[1]),
#                 style="dark",
#                 bearing=bearing,
#                 zoom=zoom,
#             ),
#             updatemenus=[
#                 dict(
#                     buttons=(  
#                         [
#                             dict(
#                                 args=[
#                                     {
#                                         "mapbox.zoom": zoom,
#                                         "mapbox.center.lon": latlon_SCO[1],
#                                         "mapbox.center.lat": latlon_SCO[0],
#                                         "mapbox.bearing": bearing,
#                                         "mapbox.style": "dark",
#                                     }
#                                 ],
#                                 label="Reset Zoom",
#                                 method="relayout",
#                             )
#                         ]
#                     ),
#                     direction="left",
#                     pad={"r": 0, "t": 0, "b": 0, "l": 0},
#                     showactive=False,
#                     type="buttons",
#                     x=0.45,
#                     y=0.02,
#                     xanchor="left",
#                     yanchor="bottom",
#                     bgcolor="#323130",
#                     borderwidth=1,
#                     bordercolor="#6d6d6d",
#                     font=dict(color="#FFFFFF"),
#                 )
#             ],
#         ),
#     )


if __name__ == "__main__":
    app.run_server(debug=True, port=8052,  threaded=True)