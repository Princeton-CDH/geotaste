from ..imports import *
from ..app.figs import *
from .datasets import *

class MemberFigure(FigureFactory):
    records_name='members'
    key = ''
    records_points_dim = 'x' # or 'y'
    dataset_class = MembersDataset

    
    @cached_property
    def figdf(self):
        if not len(self.df): return pd.DataFrame()
        return pd.DataFrame([
            {'member':member, self.key:yr}
            for member,years in zip(self.df.index, self.df[self.key])
            for yr in years
        ]).sort_values([self.key, 'member']).set_index('member')



class MemberTableFigure(MemberFigure, TableFigure):
    cols = ['name','title','gender','birth_year','death_year','nationalities']

    def plot(self, **kwargs):
        cols = self.cols if self.cols else self.df.columns
        dff = self.df[[c for c in cols if c in set(self.df.columns)]]
        for col in set(cols) & set(Members().cols_sep):
            dff[col] = dff[col].apply(lambda x: Members().sep.join(str(y) for y in x))
        return super().plot(df=dff)
    




class MemberDOBFigure(MemberFigure):
    key = 'birth_year'

    def plot(self, color=None, **kwargs):
        fig = super().plot_histogram_bar(
            x=self.key,
            color=color,
            quant=False,
            height=100
        )
        fig.update_yaxes(visible=False)
        fig.update_xaxes(title_text='')
        return fig
    
    def selected_years(self, selectedData):
        return self.selected_points_x(selectedData)
    
    

class MembershipYearFigure(MemberFigure):
    records_name='annual subscriptions'
    key='membership_years'

    

    def plot(self, color=None, **kwargs):        
        fig = super().plot_histogram_bar(
            x=self.key,
            color=color,
            quant=False,
            df=self.figdf,
            height=100,
        )
        fig.update_yaxes(visible=False)
        fig.update_xaxes(title_text='')
        return fig




class MemberGenderFigure(MemberFigure):
    key='gender'

    def plot(self, color=None, **kwargs):
        fig = super().plot_histogram_bar(
            x=self.key,
            color=color,
            # log_y=True,
            quant=False,
            height=100,
            text='count'
        )
        fig.update_yaxes(visible=False)
        fig.update_xaxes(title_text='')
        return fig




class MemberNationalityMapFigure(MemberFigure):
    records_name='member nationalities'
    key='nationalities'
    records_points_dim='locations'
    
    @cached_property
    def figdf(self):
        df = px.data.gapminder()
        d=dict(zip(df.country, df.iso_alpha))
        df=super().figdf.reset_index().set_index(self.key)
        df['iso']=d
        df['iso'].fillna('',inplace=True)
        return df.reset_index().set_index('member')
    
    def plot(self, color=None, **kwargs):
        fdf = pd.DataFrame(self.figdf['iso'].value_counts()).reset_index()
        fig = px.choropleth(
            fdf, 
            locations="iso",
            color="count",
            # color_continuous_scale='oranges' if color == RIGHT_COLOR else 'purples',
            color_continuous_scale=['rgba(64, 176, 166, 0)', RIGHT_COLOR] if color == RIGHT_COLOR else ['rgba(171, 145, 85, 0)', LEFT_COLOR],
            range_color=(0,400), #fdf['count'].min(), fdf['count'].max())
            height=300,
            template=PLOTLY_TEMPLATE
        )
        fig.update_coloraxes(showscale=False)
        fig.update_layout(
            clickmode='event+select', 
            # dragmode='select',
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        fig.update_geos(
            showframe=False,
            showcoastlines=False,
            # projection_type='mollweide'
            projection_type='miller'
        )
        return fig
    
    def selected(self, selectedData):
        if not selectedData: return {}
        isos = self.selected_points_locations(selectedData)
        xs = list(self.figdf[self.figdf.iso.isin(isos)][self.key].unique())
        return filter_series(self.series, xs, test_func=isin_or_hasone)


class MemberNationalityFigure(MemberFigure):
    records_name='member nationalities'
    key='nationalities'
    records_points_dim='y'
    
    def plot(self, color=None, **kwargs):
        df_counts = make_counts_df(self.series)        
        # category_orders={self.key: * df_counts[self.key].index}
        fig=px.bar(
            df_counts,
            y=self.key,
            x='count', 
            color_discrete_sequence=[color] if color else None,
            # range_x=(self.minval, self.maxval),
            height=len(df_counts)*20,
            text='count',
            template=PLOTLY_TEMPLATE,
            log_x=True,
            # **kwargs
        )
        cats=list(reversed(df_counts[self.key].index))
        fig.update_yaxes(categoryorder='array', categoryarray=cats)
        fig.update_traces(textposition = 'auto', textfont_size=14)
        fig.update_layout(
            uniformtext_minsize=12,
            clickmode='event+select', 
            dragmode='select',# if quant else None, 
            selectdirection='v',# if quant else None
        )
        fig.update_xaxes(title_text='Number of members', visible=False)
        fig.update_yaxes(title_text='', tickangle=0, autorange='reversed')
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return fig



class MemberMap(MemberFigure):
    def __init__(self, filter_data={}, df=None):
        super().__init__(
            df=MemberDwellings().data if df is None else df,
            filter_data=filter_data
        )

    def plot(self, color=None, height=250, **kwargs):
        # fig = px.scatter_mapbox(
        #     self.df.reset_index(), 
        #     lat='latitude',
        #     lon='longitude', 
        #     center=dict(lat=LATLON_SCO[0], lon=LATLON_SCO[1]),
        #     custom_data=['member'],
        #     zoom=12, 
        #     hover_name='name',
        #     height=height,
        #     size_max=40,
        #     template=PLOTLY_TEMPLATE
        # )
        # fig.update_traces(marker=dict(size=7))
        # if color: fig.update_traces(marker=dict(color=color))
        # fig.update_mapboxes(style="stamen-toner")
        # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        # fig = go.Figure()
        # fig.add_trace(go.Scattermapbox(
        #     lat=self.df.latitude,
        #     lon=self.df.longitude,
        #     mode='markers',
        #     marker=go.scattermapbox.Marker(
        #         size=10,
        #         color='black',
        #         opacity=1
        #     ),
        #     text=self.df.name,
        #     hoverinfo='text'
        # ))
        # fig.add_trace(go.Scattermapbox(
        #     lat=self.df.latitude,
        #     lon=self.df.longitude,
        #     mode='markers',
        #     marker=go.scattermapbox.Marker(
        #         size=7,
        #         color=color,
        #         opacity=1
        #     ),
        # ))


    # fig.add_trace(go.Scattermapbox(
    #         lat=site_lat,
    #         lon=site_lon,
    #         mode='markers',
    #         marker=go.scattermapbox.Marker(
    #             size=8,
    #             color='rgb(242, 177, 172)',
    #             opacity=0.7
    #         ),
    #         hoverinfo='none'
    #     ))

        # counts_by_arrond = pd.DataFrame(self.df.arrond_id.value_counts()).reset_index()
        counts_by_arrond = get_arrond_counts(self.df).reset_index()

        fig_choro = px.choropleth_mapbox(
            counts_by_arrond,
            geojson=get_geojson_arrondissement(),
            locations='arrond_id', 
            color='count',
            # color='perc',
            center=MAP_CENTER,
            zoom=10,
            color_continuous_scale=['rgba(64, 176, 166, 0)', RIGHT_COLOR] if color == RIGHT_COLOR else ['rgba(171, 145, 85, 0)', LEFT_COLOR],
            opacity=1,
            hover_name='arrond_id',
            hover_data=['count','perc'],
            labels='arrond_id',
            height=height,
            template=PLOTLY_TEMPLATE
        )
        fig_choro.update_mapboxes(style="white-bg")
        fig_choro.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            clickmode='event+select', 
        )
        # fig_choro.update_traces(marker_line_width=2)
        ofig = fig_choro
        ofig.update_layout(
            coloraxis=dict(
                colorbar=dict(
                    orientation='h', 
                    y=-0.25,
                    thickness=10
                )
            ),
        )
        # ofig=go.Figure(data=fig_choro.data + fig.data, layout=fig_choro.layout)
        # ofig=go.Figure(data=fig_choro.data + fig.data, layout=fig_choro.layout)
        # ofig.update_layout(autosize=True)
        # ofig.layout._config = {'responsive':True}
        return ofig

    def selected(self, selectedData):
        if selectedData:
            latlons = self.selected_points_latlon(selectedData)
            if latlons:
                s=pd.Series(list(zip(self.df['latitude'], self.df['longitude'])), name='latlon', index=self.df.index)
                matches = self.selected_points_customdata(selectedData)
                members = [m[0] for m in matches if m]
                return filter_series(
                    s, 
                    latlons, 
                    test_func=isin_or_hasone, 
                    matches=members
                )
            else:
                locations = self.selected_points_locations(selectedData)
                print('locations',locations)
                if locations:
                    s=self.df[['arrond_id']].reset_index().drop_duplicates().set_index(self.df.index.name)['arrond_id']
                    o=filter_series(s, locations, test_func=isin_or_hasone)
                    print(o)
                    return o
            
        return {}

        










class ComparisonMemberMap(MemberMap):
    cols_table = ['name','membership_years','birth_year','gender','nationalities','arrond_id','L_or_R']
    

    def __init__(
            self, 
            filter_data_L={}, 
            filter_data_R={}, 
            df=None):

        if not filter_data_L and not filter_data_R:
            super().__init__()
            self.df['L_or_R'] = 'Both'
        else:    
            filter_data_comparison = compare_filters(
                filter_data_L if filter_data_L else self.filter_data_total, 
                filter_data_R if filter_data_R else self.filter_data_total,
            )
            super().__init__(filter_data = filter_data_comparison)

    @property
    def filter_data_total(self):
        return {
            INTENSION_KEY:{},
            EXTENSION_KEY:{i:{} for i in Members().data.index}
        }

    @cached_property
    def df_arronds(self):
        df_L = self.df[self.df.L_or_R.isin({'L','Both'})]
        df_R = self.df[self.df.L_or_R.isin({'R','Both'})]
        df_arronds = compare_arrond_counts(df_L, df_R)
        return df_arronds

    def plot(self, height=250, **kwargs):
        def get_color(x):
            if x.startswith('L'): return LEFT_COLOR
            if x.startswith('R'): return RIGHT_COLOR
            return BOTH_COLOR
        
        color_map = {label:get_color(label) for label in self.df['L_or_R'].apply(str).unique()}
        fig = px.scatter_mapbox(
            self.df, 
            lat='latitude',
            lon='longitude', 
            center=dict(lat=LATLON_SCO[0], lon=LATLON_SCO[1]),
            zoom=12, 
            hover_name='name',
            color='L_or_R',
            color_discrete_map=color_map,
            # height=height,
            size_max=40,
            template=PLOTLY_TEMPLATE
            # **kwargs
        )
        fig.update_traces(marker=dict(size=10))
        fig.update_mapboxes(style='stamen-toner')
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        fig_choro = px.choropleth_mapbox(
            self.df_arronds.reset_index(),
            geojson=get_geojson_arrondissement(),
            locations='arrond_id', 
            color='perc_L->R',
            center=MAP_CENTER,
            zoom=12,
            # color_continuous_scale='puor',
            color_continuous_scale=[LEFT_COLOR, 'rgba(0,0,0,0)', RIGHT_COLOR],
            opacity=.5,
            # height=height,
            template=PLOTLY_TEMPLATE
        )
        fig_choro.update_mapboxes(style="stamen-toner")
        fig_choro.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        fig_choro.update_layout(
            coloraxis=dict(
                colorbar=dict(
                    orientation='h', 
                    y=0,
                    thickness=10
                )
            ),

        )
        
        # fig_choro.update_coloraxes(reversescale=True)
        ofig=go.Figure(
            data=fig_choro.data + fig.data, 
            layout=fig_choro.layout
        )
        ofig.update_layout(autosize=True)
        ofig.layout._config = {'responsive':True}
        return ofig
    
    def table(self, cols=[], sep=' ', **kwargs):
        df = pd.DataFrame(
            g.assign(
                arrond_id=sep.join(
                    sorted(
                        [x for x in g.arrond_id.unique() if x]
                        , key=lambda x: int(x)
                    )
                )
            ).iloc[0] 
            for i,g in self.df.groupby(['uri','L_or_R'])
        )
        return get_dash_table(df, cols=list(self.cols_table if not cols else cols))
    
    def table_arrond(self, cols=[], **kwargs):
        cols = ['arrond_id', 'count_L', 'count_R', 'perc_L', 'perc_R', 'perc_L->R']
        return get_dash_table(self.df_arronds, cols=cols, page_size=5)
    
    def table_diff(self, cols=[], **kwargs):
        return get_dash_table(self.rank_diff())#, cols=['key_L', 'key_R', 'pvalue', 'statistic', 'is_self'])
            
    def diffdb(self):
        from sqlitedict import SqliteDict
        return SqliteDict(os.path.join(PATH_DATA, 'diffdb.sqlitedict'))

    def diffkeys(self):
        return tuple(sorted(list(json.dumps(d, sort_keys=True) for d in self.filter_data.get(INTENSION_KEY,({},{})))))

    def measure_diff(self, force=False):
        name_L,name_R = self.diffkeys()
        # if name_L == name_R: return {}
        key = json.dumps([name_L, name_R])
        
        with self.diffdb() as cache:    
            if force or not key in cache:
                from scipy.stats import kstest
                stat = kstest(self.df_arronds.count_L, self.df_arronds.count_R)
                # stat = kstest(self.df_arronds.perc_L, self.df_arronds.perc_R)
                cache[key]={k:getattr(stat,k) for k in dir(stat) if k and k[0]!='_' if k not in {'count','index'}}
                cache.commit()
            return cache[key]


    def get_diffs(self):
        ld=[]
        with self.diffdb() as cache: 
            for key,val in cache.items():
                k1,k2=json.loads(key)
                ld.append(dict(group1=k1, group2=k2, **{kx:float(kv) for kx,kv in dict(val).items()}))
        df=pd.DataFrame(ld)
        df=df.sort_values('statistic',ascending=False) if len(df) else df
        return df

    def rank_diff(self):
        res = self.measure_diff()
        df = self.get_diffs()
        df['is_self']=[((k1,k2) == self.diffkeys()) for k1,k2 in zip(df.group1, df.group2)]
        return df





class ComparisonMemberTable(TableFigure):
    cols = ['arrond_id', 'count_L', 'count_R', 'perc_L', 'perc_R', 'perc_L->R']
    
    def plot(self, **kwargs):
        cols=self.cols
        dff = self.df[cols]
        cols_l = [{'id':col, 'name':col.replace('_',' ').title()} for col in cols]

        return dash_table.DataTable(
            data=dff.to_dict('records'),
            columns=cols_l,
            sort_action="native",
            # sort_mode="multi",
            # filter_action="native",
            # page_action="native",
            # page_size=5,
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
        )








class MemberArrondMap(MemberFigure):
    def __init__(self, filter_data={}, df=None):
        super().__init__(
            df=MemberDwellings().data if df is None else df,
            filter_data=filter_data
        )

    def plot(self, color=None, height=250, **kwargs):
        import geopandas as gpd

        counts_by_arrond = get_arrond_counts(self.df).reset_index()

        geojson = get_geojson_arrondissement()
        gdf = (
            gpd.GeoDataFrame.from_features(geojson)
            .merge(counts_by_arrond, on="arrond_id")
            .assign(lat=lambda d: d.geometry.centroid.y, lon=lambda d: d.geometry.centroid.x)
            .set_index("arrond_id", drop=False)
        )

        fig_choro = px.choropleth_mapbox(
            counts_by_arrond,
            geojson=geojson,
            locations='arrond_id', 
            color='count',
            center=MAP_CENTER,
            zoom=10,
            color_continuous_scale=['rgba(64, 176, 166, 0)', RIGHT_COLOR] if color == RIGHT_COLOR else ['rgba(171, 145, 85, 0)', LEFT_COLOR],
            opacity=.5,
            hover_name='arrond_id',
            hover_data=['count','perc'],
            labels='arrond_id',
            height=height,
            template=PLOTLY_TEMPLATE,
            mapbox_style='white-bg',
            # mapbox_style='mapbox://styles/ryanheuser/cljef7th1000801qu6018gbx8'
        )
        fig_choro.update_traces(marker_line_width=2)

        # fig_choro.add_scattermapbox(
        #     lon=gdf.lon,
        #     lat=gdf.lat,
        #     mode='text',
        #     text=gdf.arrond_id,
        #     hoverinfo='none'

        # )
        ofig = fig_choro

        ofig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            clickmode='event+select', 
            dragmode=False,
        )
        ofig.update_coloraxes(colorbar=dict(orientation='h', y=-0.25, thickness=10))
        ofig.update_xaxes(fixedrange = True)
        ofig.update_yaxes(fixedrange = True)
        return ofig
    
    def selected(self, selectedData):
        if selectedData:
            locations = self.selected_points_locations(selectedData)
            if locations:
                s=self.df[['arrond_id']].reset_index().drop_duplicates().set_index(self.df.index.name)['arrond_id']
                o=filter_series(s, locations, test_func=isin_or_hasone)
                return o
        
        return {}