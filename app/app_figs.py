from app_imports import *



##################################################
# COMPONENTS
##################################################


def plot_members_map(
        df = None,
        ):
    if df is None: 
        df = MemberDwellingsDataset().data.reset_index()

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
        lat="latitude", 
        lon="longitude", 
        center=dict(lat=LATLON_SCO[0], lon=LATLON_SCO[1]),
        # hover_name="member_id", 
        # color='arrrondissement',
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
            # pitch=45
        ),
    )
    fig.update_traces(marker=dict(size=6, color='#811818'))
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig
    # return go.Figure(data=fig_choro.data + fig.data, layout = fig.layout)

def plot_members_dob():
    fig=px.histogram(Members().data, 'birth_year', height=200)
    fig.update_layout(
        clickmode='event+select', 
        dragmode='select', 
        selectdirection='h',
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    return fig



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






class FigureFactory:
    def __init__(self, df):
        self.df = df

    @staticmethod
    def filter_query(filter_data={}):
        def join_query(ql, operator='and'):
            if len(ql)>1:
                q=f' {operator} '.join(f'({qlx})' for qlx in ql)
            elif len(ql)==1:
                q=ql[0]
            else:
                q=''
            return q


        # preproc/clean
        if not filter_data: filter_data={}
        for k,v in list(filter_data.items()):
            if v is None:
                del filter_data[k]    
        
        # something there?
        q=''
        if filter_data:
            ql=[]
            for k,v in filter_data.items():
                qx=''
                if is_l(v):
                    if v and is_l(v[0]):
                        qx = [
                            f'{minv}<={k}<={maxv}'
                            for minv,maxv in iter_minmaxs(v)
                        ]
                    else:
                        qx = [
                            f'{k}=={vx}' if type(vx) in {int,float} else f'{k}=="{vx}"'
                            for vx in v
                        ]
                elif type(v)==str:
                    qx=[f'{k}=="{v}"']
                
                if qx: ql.append(join_query(qx, operator='or'))
            q=join_query(ql, operator='and')        
        return q
    
    def filter_df(self, filter_data={}, q=None):
        q=self.filter_query(filter_data) if not q else q
        df=self.df if not q else self.df.query(q)
        return df
    
    def filter(self, filter_data={}):
        df=self.filter_df(filter_data)
        return FigureFactory(df)
    
    def plot_biplot(self, x_axis, y_axis, qual_col):
        return px.scatter(
            self.df,
            x=x_axis,
            y=y_axis,
            color=qual_col,
            template='plotly_dark',
            # trendline="ols",
            # trendline_color_override="orange",
            # trendline_scope='overall',
            # trendline_options=dict(frac=0.1)
            marginal_x='box',
            marginal_y='box'
        )
    
    def plot_parcoords(self, cols=None):
        fdf=self.df[cols] if cols else self.df
        fig=px.parallel_coordinates(
            fdf,
            width=len(fdf.columns) * 150,
        )
        fig.update_layout(
            autosize=False,
            width=len(fdf.columns) * 150,
            # height=500,
            # xaxis=dict(
            #     rangeslider=dict(
            #         visible=True),
            #         type="linear"
            #     )
        )
        # fig.update_traces(color_discrete_map=ColorDict())
            
        # fig.update_traces(labelangle=-90)
        # fig.update_xaxes(tickangle=-90)
        # fig.update_yaxes(tickangle=-90)
        return fig
    
    def plot_map(self, color='mean_household_inc', mapbox_style='carto-darkmatter',opacity=.5,**kwargs):
        fig=px.choropleth_mapbox(
            self.df,
            locations='prec_20',
            geojson=get_geojson_warddiv(),
            featureidkey='id',
            color=color,
            mapbox_style=mapbox_style,
            center=get_center_lat_lon(),
            # height=800,
            zoom=11,
            opacity=opacity,
            color_discrete_map=ColorDict(),
            **kwargs
            
        )
        fig.update_mapboxes(pitch=60)#, bearing=50)

        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            # mapbox_style='mapbox://styles/mapbox-map-design/ckhqrf2tz0dt119ny6azh975y',
            # mapbox_layers=[
            #     {
            #         "below": 'traces',
            #         "sourcetype": "raster",
            #         "source": [
            #             "mapbox://mapbox.mapbox-terrain-dem-v1"
            #         ]
            #     }
            # ]
        )    

        return fig
    



def is_l(x): return type(x) in {list,tuple}
def iter_minmaxs(l):
    if is_l(l):
        for x in l:
            if is_l(x):
                if len(x)==2 and not is_l(x[0]) and not is_l(x[1]):
                    yield x
                else:
                    yield from iter_minmaxs(x)
