from app_imports import *


## Setup plotly
# Plotly mapbox public token
mapbox_access_token = open(os.path.expanduser('~/.mapbox_token')).read()
px.set_mapbox_access_token(mapbox_access_token)



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
        height=600,
        # legend=False
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
        page_action="native",
        page_size=5
        
    )





def get_map_graph():
    return dcc.Graph(
        id='members-map',
        className='div-for-charts map-graph',
        figure=DashMembersMap()
    )

def get_map_table():
    return dmc.Container(
        DashMembersDataTable(),
        className='datatbl-container',
        # fluid=True
        # size='xl'
    )

def get_table_html(df, className='', **kwargs):
    defaults=dict(
        striped=True,
        highlightOnHover=True,
        withBorder=True,
        withColumnBorders=True,
    )
    columns, values = df.columns, df.values
    header = [html.Tr([html.Th(col) for col in columns])]
    rows = [html.Tr([html.Td(cell) for cell in row]) for row in values]
    table = [html.Thead(header), html.Tbody(rows)]
    return dmc.Table(
        children=table,
        className='table '+className,
        **{**defaults, **kwargs}
    )



def get_map_table_html(dff=None):
    dff = get_filtered_data_members().sample(10) if dff is None else dff
    return dmc.Container(get_table_html(dff))