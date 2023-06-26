from ..imports import *


##################################################
# COMPONENTS
##################################################


class FigureFactory(DashFigureFactory):
    records_name = 'records'
    key = ''
    records_points_dim = 'xy'
    dataset_class = None

    @cached_property
    def dataset(self): return self.dataset_class() if self.dataset_class is not None else None
    @cached_property
    def data(self):
        dset = self.dataset
        return dset.data if dset is not None else pd.DataFrame()
    @cached_property
    def series(self):
        if self.key and len(self.data) and self.key in set(self.data.columns): 
            return self.data[self.key]
        return pd.Series()
        
    def __init__(self, filter_data={}, df=None, **kwargs):
        if filter_data is None: filter_data = {}
        self.filter_data = filter_data
        self._data = data = self.data
        self._df = df if df is not None else data



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
        return self.selected_points_key(selectedData, key)
    
    def selected_points_customdata(self, selectedData, key='customdata'):
        return self.selected_points_key(selectedData, key)
    
    
    def selected_points_key(self, selectedData, key):
        return [
            d.get(key,'') 
            for d in selectedData.get('points',[]) 
            if d 
            and key in d 
            and d[key]
        ]

    
    def selected_points_latlon(self, selectedData, keys=('lat', 'lon')):
        return [(d.get(keys[0],np.nan), d.get(keys[1],np.nan)) for d in selectedData.get('points',[]) if keys[0] in d and keys[1] in d]
    
    def selected(self, selectedData):
        print('selectedData', selectedData)
        if not selectedData: return {}
        xs = self.selected_points(selectedData) 
        if not xs: return {}
        return filter_series(self.series, xs, test_func=isin_or_hasone)
    
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
        return pd.Series(flatten_list(s))
    
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
            template=PLOTLY_TEMPLATE,
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
            template=PLOTLY_TEMPLATE,
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
            y='count',
            color=None, 
            df=None, 
            height=100, 
            quant=None, 
            category_orders=None, 
            series=None,
            series_name=None,
            keep_missing_types=True,
            **kwargs):
        
        # figdf = self.get_figdf(x,quant=False)
        if series is None:
            if df is None: df = self.df
            if not x in set(df.columns): return go.Figure()
            l=flatten_list(df[x])
        else:
            l = series

        l = [x if x!='' else UNKNOWN for x in l]
        series = pd.Series(l, name=x if not series_name else series_name)
        s=series.value_counts()

        # make sure all types are there
        if keep_missing_types:
            vals = [x if x!='' else UNKNOWN for x in self.vals]
            missing_valtypes = set(vals) - set(s.index)
            for xval in missing_valtypes: s[xval]=0
            s=s.sort_index()

        df_counts = pd.DataFrame(s).reset_index()
        if not quant and category_orders is None:
            category_orders = {self.key:df_counts.index}
        
        fig=px.bar(
            df_counts,
            x=x,
            y=y, 
            height=height,
            color_discrete_sequence=[color] if color else None,
            category_orders=category_orders,
            range_x=(self.minval, self.maxval),
            template=PLOTLY_TEMPLATE,
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
            height=400,
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
            height=height,
            size_max=40,
            # **kwargs
        )
        if mapbox_style: mapbox_opts['style']=mapbox_style
        fig.update_layout(mapbox=mapbox_opts)
        # fig.update_traces(marker=dict(size=6, color='#811818'))
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return fig
    




    


class TableFigure(FigureFactory):
    cols = []

    def plot(self, df=None, cols=[], page_size=5, **kwargs):
        df = df if df is not None else self.df
        cols = cols if cols else (self.cols if self.cols else df.columns)
        dff = df[cols]
        cols_l = [{'id':col, 'name':col.replace('_',' ').title()} for col in cols]

        return dash_table.DataTable(
            data=dff.to_dict('records'),
            columns=cols_l,
            sort_action="native",
            sort_mode="multi",
            filter_action="native",
            page_action="native",
            page_size=page_size,
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
        )
    
