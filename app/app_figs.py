from app_imports import *



##################################################
# COMPONENTS
##################################################


def plot_members_map(
        df = None,
        members = {},
        ):
    if df is None: df = MemberDwellingsDataset().data.reset_index()
    df = filter_figdf(df)
    if members: df = df[df.member.isin(members)]

    # fig_choro = px.choropleth_mapbox(
    #     df,
    #     geojson=get_geojson_arrondissement(),
    #     locations='arrrondissement', 
    #     color='arrrondissement',
    #     center=dict(lat=LATLON_SCO[0], lon=LATLON_SCO[1]),
    #     zoom=12,
    #     opacity=.1
    # )
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig = px.scatter_mapbox(
        df, 
        lat="lat", 
        lon="lon", 
        center=dict(lat=LATLON_SCO[0], lon=LATLON_SCO[1]),
        # hover_name="member_id", 
        color='arrrondissement',
        # hover_data=["State", "Population"],
        # color_discrete_sequence=["fuchsia"], 
        zoom=12, 
        hover_name='name',
        # hover_data=['uri', 'title', 'gender', 'has_card', 'birth_year', 'death_year', 'membership_years'],
        height=600,
        size_max=40
    )
    fig.update_layout(
        mapbox=dict(
            style="stamen-toner",
            pitch=45
        ),
    )
    fig.update_traces(marker=dict(size=10))
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return [fig]    
    # return go.Figure(data=fig_choro.data + fig.data, layout = fig.layout)



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
        id='members-tbl',
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


def filter_figdf(figdf):
    figdf['lat']=pd.to_numeric(figdf['latitude'], 'coerce')
    figdf['lon']=pd.to_numeric(figdf['longitude'], 'coerce')
    return figdf[figdf.lat.notna() & figdf.lon.notna()]