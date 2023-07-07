from .imports import *


###########
# Figures #
###########

class PlotlyFigureSelector:
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
        logger.debug('selectedData')
        if not selectedData: return {}
        xs = self.selected_points(selectedData) 
        if not xs: return {}
        return filter_series(self.series, xs, test_func=isin_or_hasone)
    
    def selected_records(self, selectedData):
        return set(self.selected(selectedData).index)





class FigureFactory(DashFigureFactory, PlotlyFigureSelector, Logmaker):
    records_name = 'records'
    key = ''
    records_points_dim = 'xy'
    dataset_class = CombinedDataset
    drop_duplicates = ()
    quant = None
    opts_xaxis=dict()
    opts_yaxis=dict()
    height=600
    color=None
    min_series_val=None
    max_series_val=None
    
    def __init__(self, filter_data={}, df=None, **kwargs):
        if filter_data is None: filter_data = {}
        self.filter_data = filter_data

    @cached_property
    def dataset(self): 
        return (self.dataset_class() if self.dataset_class is not None else None)

    @cached_property
    def data_all(self):
        odf=(
            self.dataset.data 
            if self.dataset is not None and self.dataset.data is not None
            else pd.DataFrame()
        )
        if self.drop_duplicates and len(odf):
            odf=odf.drop_duplicates(self.drop_duplicates)
        return odf
    
    @cached_property
    def data(self):
        return filter_df(self.data_all, self.filter_data)
    
    @property
    def filter_desc(self):
        return format_intension(self.filter_data.get(INTENSION_KEY,{}))
    
    @cached_property
    def series(self): return self.get_series(df=self.data)
    @cached_property
    def series_q(self): return self.get_series(df=self.data, quant=True)
    @cached_property
    def series_all(self): return self.get_series(df=self.data_all)
    @cached_property
    def series_all_q(self): return self.get_series(df=self.data_all, quant=True)
    
    def get_series(self, key=None, df=None, quant=None):
        if key is None: key=self.key
        if not key: 
            return pd.Series(name=key)
        if df is None: df=self.data
        if not len(df) or not key in set(df.columns): 
            return pd.Series(name=key)
        s=pd.Series(
            qualquant_series(
                flatten_series(df[key]),
                quant=quant if quant is not None else self.quant
            ),
            name=self.key
        )
        if self.min_series_val is not None: s=s[s>=self.min_series_val]
        if self.max_series_val is not None: s=s[s<=self.max_series_val]
        return s
    
        
    @cached_property
    def minval(self): return self.series.min()
    
    @cached_property
    def maxval(self): return self.series.max()

    @cached_property
    def query_str(self) -> str:
        return to_query_string(self.filter_data)
    
    @cached_property
    def filtered(self): return bool(self.filter_data)

    

    @cached_property
    def df(self) -> pd.DataFrame:
        return self.data
    
    @cached_property
    def figdf(self) -> pd.DataFrame:
        if not len(self.df): return pd.DataFrame()
        iname = self.df.index.name
        return pd.DataFrame([
            {iname:i, self.key:v}
            for i,vals in zip(self.df.index, self.df[self.key])
            for v in flatten_list(vals)
        ]).sort_values([self.key, iname]).set_index(iname)
    
    
        

        
    def plot_histogram(
            self, 
            color=None, 
            height=None, 
            keep_missing_types=True,
            **kwargs):
        
        height = self.height if height is None else height
        color = self.color if color is None else color
        valtypes = (self.series_all if keep_missing_types else self.series).unique()
        vals = self.series
        valcounts = vals.value_counts()
        for mv in set(valtypes)-set(vals): valcounts[mv]=0
        df_counts = pd.DataFrame(valcounts).reset_index()
        category_orders = {self.key:df_counts.index} if self.quant is False else None
        
        fig=px.bar(
            df_counts,
            x=self.key,
            y='count', 
            height=height,
            color_discrete_sequence=[color] if color else None,
            category_orders=category_orders,
            # range_x=(self.minval, self.maxval),
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
        if self.opts_xaxis: fig.update_xaxes(**self.opts_xaxis)
        if self.opts_yaxis: fig.update_yaxes(**self.opts_yaxis)
        return fig




class TypicalFigure(FigureFactory):
    height = 100
    plot = FigureFactory.plot_histogram
    opts_xaxis=dict(title_text='')
    opts_yaxis=dict(visible=False)

class MemberFigure(TypicalFigure):
    records_name='members'
    drop_duplicates=('member',)
    pass

class MemberDOBFigure(MemberFigure):
    key = 'member_dob'
    quant = True




class MembershipYearFigure(MemberFigure):
    records_name='annual subscriptions'
    key='member_membership'
    quant = True


class MemberGenderFigure(MemberFigure):
    key='member_gender'
    quant=False
    

class MemberNationalityFigure(MemberFigure):
    records_name='member nationalities'
    key='member_nationalities'
    # records_points_dim='y'
    
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


class MemberArrondMap(MemberFigure):
    def plot(self, color=None, height=250, **kwargs):
        counts_by_arrond = get_arrond_counts(self.df).reset_index()
        geojson = get_geojson_arrondissement()
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


        # add labels? doesn't work on remote version??
        # import geopandas as gpd
        # gdf = (
        #     gpd.GeoDataFrame.from_features(geojson)
        #     .merge(counts_by_arrond, on="arrond_id")
        #     .assign(lat=lambda d: d.geometry.centroid.y, lon=lambda d: d.geometry.centroid.x)
        #     .set_index("arrond_id", drop=False)
        # )
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






#### BOOKS

class BookFigure(TypicalFigure):
    records_name='books'
    drop_duplicates=('book',)

class BookYearFigure(BookFigure):
    key = 'book_year'
    quant = True
    min_series_val=1800
    max_series_val=1950




### CREATORS

class CreatorFigure(TypicalFigure):
    records_name='creators'
    drop_duplicates=('creator',)

class CreatorGenderFigure(CreatorFigure):
    key='creator_gender'
    quant=False

