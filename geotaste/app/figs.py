from .imports import *



##################################################
# COMPONENTS
##################################################


class FigureFactory(DashFigureFactory):
    records_name = 'records'
    key = ''
    records_points_dim = 'xy'

    def __init__(self, filter_data = {}, df = None):
        if filter_data is None: filter_data = {}
        self.filter_data = filter_data
        self._df = df
        self._data = self._df # overwrite



    # def filter_df(self, filter_data):
    #     if self.key in filter_data: 
    #         fd=filter_data[self.key]

    def selected_points_xy(self, selectedData):
        return [(d.get('x',np.nan), d.get('y',np.nan)) for d in selectedData.get('points',[]) if d]
    
    def selected_points_x(self, selectedData):
        return [x for x,y in self.selected_points_xy(selectedData)]
    
    def selected_points_y(self, selectedData):
        return [y for x,y in self.selected_points_xy(selectedData)]
    
    def selected_points(self, selectedData):
        func = getattr(self, f'selected_points_{self.records_points_dim}')
        return func(selectedData)
    
    def selected_points_locations(self, selectedData, key='location'):
        return [d.get(key,'') for d in selectedData.get('points',[]) if d and key in d and d[key]]
    
    def selected_points_latlon(self, selectedData, keys=('lat', 'lon')):
        return [(d.get(keys[0],np.nan), d.get(keys[1],np.nan)) for d in selectedData.get('points',[]) if keys[0] in d and keys[1] in d]
    
    def selected(self, selectedData):
        if not selectedData: return {}

        xs = self.selected_points(selectedData) 
        if not xs: return {}

        series = self.series[self.series.apply(lambda x: isin_or_hasone(x, xs))]
        od = dict(series)
        return {'intension':{self.key:xs} if self.key else xs, 'extension':od}

    
    def selected_records(self, selectedData):
        return set(self.selected(selectedData).index)




    @cached_property
    def df(self) -> pd.DataFrame:
        if self._df is None: return pd.DataFrame()
        odf = filter_df(self._df, self.filter_data)
        return odf
    
    @cached_property
    def series(self) -> pd.Series:
        try:
            return self._df[self.key]
        except KeyError:
            return pd.Series()
        
    @cached_property
    def vals(self):
        l = []
        try:
            s=self._data[self.key]
        except KeyError:
            return pd.Series()
        for x in s:
            if is_listy(x):
                l+=list(x)
            else:
                l+=[x]
        return pd.Series(l)
    
    @cached_property
    def vals_q(self):
        return pd.to_numeric(self.vals, errors='coerce')
        
    @cached_property
    def series_q(self):
        return pd.to_numeric(self.series,errors='coerce')
    
    @cached_property
    def minval(self): return self.vals_q.min()
    
    @cached_property
    def maxval(self): return self.vals_q.max()

    @cached_property
    def query_str(self) -> str:
        return to_query_string(self.filter_data)
    
    @cached_property
    def filtered(self): return bool(self.filter_data)

    @cached_property
    def filter_desc(self):
        if not self.filtered:
            return f'All {len(self._df):,} {self.records_name}.'
        else:
            return f'Filtering {self.query_str} yields {len(self.df):,} of {len(self._df):,} {self.records_name}.'
        
    def get_figdf(self, x, quant=None, df=None):
        figdf=(df if df is not None else self.df).sample(frac=1)
        if quant is True: 
            figdf[x] = pd.to_numeric(figdf[x], errors='coerce')
        elif quant is False:
            figdf[x] = figdf[x].fillna('').apply(str)
        return figdf
    
    def plot_biplot(self, x, y, qual_col):
        return px.scatter(
            self.df,
            x=x,
            y=y,
            color=qual_col,
            template='plotly_dark',
            # trendline="ols",
            # trendline_color_override="orange",
            # trendline_scope='overall',
            # trendline_options=dict(frac=0.1)
            marginal_x='box',
            marginal_y='box'
        )
    
    def plot_histogram(self, x, color=None, df=None, height=200, quant=False, category_orders=None, **kwargs):
        figdf=(df if df is not None else self.df).sample(frac=1)
        if quant: 
            figdf[x] = pd.to_numeric(figdf[x], errors='coerce')
        elif category_orders is None:
            category_orders={self.key:figdf[self.key].value_counts().index}
        fig=px.histogram(
            figdf,
            x, 
            height=height,
            color_discrete_sequence=[color] if color else None,
            template='simple_white',
            category_orders=category_orders,
            range_x=(self.minval, self.maxval),
            **kwargs
        )
        fig.update_layout(
            clickmode='event+select', 
            dragmode='select',# if quant else None, 
            selectdirection='h',# if quant else None
        )

        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            xaxis = { 'fixedrange': True },
            yaxis = { 'fixedrange': True },
        )
        return fig
    


    def plot_histogram_bar(
            self, 
            x, 
            color=None, 
            df=None, 
            height=100, 
            quant=None, 
            category_orders=None, 
            **kwargs):
        
        # figdf = self.get_figdf(x,quant=False)
        if df is None: df = self.df
        df_counts = pd.DataFrame(df[x].value_counts()).reset_index()

        if quant is False and category_orders is None:
            category_orders = {self.key:df_counts.index}
        
        
        fig=px.bar(
            df_counts,
            x=x,
            y='count', 
            height=height,
            color_discrete_sequence=[color] if color else None,
            template='simple_white',
            category_orders=category_orders,
            range_x=(self.minval, self.maxval),
            **kwargs
        )
        fig.update_layout(
            clickmode='event+select', 
            dragmode='select',# if quant else None, 
            selectdirection='h',# if quant else None
        )

        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            xaxis = { 'fixedrange': True },
            yaxis = { 'fixedrange': True },
        )
        return fig



    
    def plot_parcoords(self, cols=None):
        fdf=self.df[cols] if cols else self.df
        fig=px.parallel_coordinates(
            fdf,
            width=len(fdf.columns) * 150,
        )
        fig.update_layout(
            autosize=False,
            width=len(fdf.columns) * 150,
        )
        return fig
    
    def plot_map(
            self,
            lat="latitude",
            lon="longitude",
            center=None,
            color=None,
            mapbox_style='stamen-toner',
            mapbox_opts={},
            zoom=12,
            **kwargs):
        
        # print(color,'color???')
        fig = px.scatter_mapbox(
            self.df, 
            lat=lat,
            lon=lon, 
            center=center,
            color=color,
            # hover_name="member_id", 
            # color='arrrondissement',
            # hover_data=["State", "Population"],
            zoom=zoom, 
            height=400,
            size_max=40,
            # **kwargs
        )
        if mapbox_style: mapbox_opts['style']=mapbox_style
        fig.update_layout(mapbox=mapbox_opts)
        # fig.update_traces(marker=dict(size=6, color='#811818'))
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return fig
    





class MemberFigure(FigureFactory):
    records_name='members'
    key = ''
    records_points_dim = 'x' # or 'y'

    def __init__(self, filter_data={}, df=None): 
        data = Members().data
        super().__init__(
            df=data if df is None else df,
            filter_data=filter_data
        )
        self._data = data

    
    @cached_property
    def figdf(self):
        if not len(self.df): return pd.DataFrame()
        return pd.DataFrame([
            {'member':member, self.key:yr}
            for member,years in zip(self.df.index, self.df[self.key])
            for yr in years
        ]).sort_values([self.key, 'member']).set_index('member')





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


class MemberNationalityFigure(MemberFigure):
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
            color_continuous_scale=px.colors.sequential.Purples,
            range_color=(0,400), #fdf['count'].min(), fdf['count'].max())
            height=300,
        )
        fig.update_coloraxes(showscale=False)
        fig.update_layout(
            clickmode='event+select', 
            dragmode='select',
            margin={"r":0,"t":0,"l":0,"b":0}
        )
        fig.update_geos(
            showframe=False,
            showcoastlines=False,
            projection_type='mollweide'
        )
        return fig
    
    def selected(self, selectedData):
        if not selectedData: return {}
        isos = self.selected_points_locations(selectedData)
        xs = list(self.figdf[self.figdf.iso.isin(isos)][self.key].unique())
        series = self.series[self.series.apply(lambda x: isin_or_hasone(x, xs))]
        return {INTENSION_KEY:{self.key:xs} if self.key else xs, EXTENSION_KEY:dict(series)}
    




class MemberDwellingsFigure(FigureFactory):
    def __init__(self, filter_data={}, df=None):
        super().__init__(
            df=MemberDwellings().data if df is None else df,
            filter_data=filter_data
        )


class MemberMap(MemberDwellingsFigure):
    def plot(self, color=None, **kwargs):
        fig = super().plot_map(
            center=dict(lat=LATLON_SCO[0], lon=LATLON_SCO[1]),
            zoom=12, 
            hover_name='name',
            **kwargs
        )
        fig.update_layout(
            mapbox=dict(
                style="stamen-toner",
                # pitch=45
            ),
        )
        if color: fig.update_traces(marker=dict(size=10, color=color))
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return fig
        # return go.Figure(data=fig_choro.data + fig.data, layout = fig.layout)

    def selected(self, selectedData):
        if not selectedData: return {}
        latlons = self.selected_points_latlon(selectedData)
        df = self.df.sample(frac=1)
        key='latlon'
        df[key]=list(zip(df['latitude'], df['longitude']))
        df = df[df.latlon.isin(latlons)]
        series = df[key]
        o = {INTENSION_KEY:{key:[]}, EXTENSION_KEY:dict(series)}
        return o



















class ComparisonFigureFactory(FigureFactory):
    def __init__(self, filter_data_L={}, filter_data_R={}, df=None):
        super().__init__(df=MemberDwellings().data if df is None else df)
        self.filter_data_L = filter_data_L
        self.filter_data_R = filter_data_R
    @cached_property
    def df_L(self): return filter_df(self._df, self.filter_data_L)
    @cached_property
    def df_R(self): return filter_df(self._df, self.filter_data_R)

    @cached_property
    def df(self):
        ids_L = set(self.df_L.index)
        ids_R = set(self.df_R.index)
        ids_both = ids_L & ids_R
        ids_only_L = ids_L - ids_R
        ids_only_R = ids_R - ids_L
        
        df_both = self.df_L.loc[list(ids_both)].assign(present_in='Both', present_in_str = f'Both')
        df_only_L = self.df_L.loc[list(ids_only_L)].assign(present_in='Left', present_in_str=f'Left ({to_query_string(self.filter_data_L)})')
        df_only_R = self.df_R.loc[list(ids_only_R)].assign(present_in='Right', present_in_str=f'Right ({to_query_string(self.filter_data_R)})')
        df = pd.concat([df_only_L, df_both, df_only_R])
        return df    



class MemberComparisonFigureFactory(ComparisonFigureFactory):
    def plot_map(self, **kwargs):

        def get_color(x):
            if x.startswith('Left'): return LEFT_COLOR
            if x.startswith('Right'): return RIGHT_COLOR
            return BOTH_COLOR
        
        figdf = self.df.sample(frac=1)
        color_map = {label:get_color(label) for label in figdf.present_in_str.apply(str).unique()}
        # print(color_map)

        fig = px.scatter_mapbox(
            self.df,
            lat='latitude',
            lon='longitude', 
            center=dict(lat=LATLON_SCO[0], lon=LATLON_SCO[1]),
            zoom=12, 
            hover_name='name',
            color='present_in_str',
            # hover_data=["State", "Population"],
            height=600,
            size_max=40,
            mapbox_style="stamen-toner",
            color_discrete_map=color_map,
            **kwargs
        )
        fig.update_traces(marker=dict(size=10))
        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        return fig
    
