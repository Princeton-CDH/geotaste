from .imports import *

cols_members=[
    'member_name_nice',
    'member_dob',
    'member_dod',
    'member_nationalities',
    'member_gender',
    'num_borrows',
    'dwelling_address',
    'member_url'
]

cols_books = [
    'author_name',
    'book_title',
    'book_year',
    # 'num_borrows_overall',
    # 'book_url'
]


###########
# Figures #
###########

class FigureFactory(DashFigureFactory, Logmaker):
    records_name = 'records'
    key = ''
    records_points_dim = 'xy'
    dataset_class = Combined
    drop_duplicates = ()
    quant = False
    opts_xaxis=dict()
    opts_yaxis=dict()
    height=600
    min_series_val=None
    max_series_val=None
    color=None 
    keep_missing_types=True
    vertical=False
    log_x=False
    log_y=False
    text=None
    
    def __init__(self, filter_data={}, selected=[], name='FigureFactory', **kwargs):
        self.name=name
        if filter_data is None: filter_data = {}
        self.filter_data = filter_data
        self.selection_data = (
            selected 
            if type(selected) is dict
            else (
                {self.key:selected}
                if self.key
                else {}
            ) 
        )
        self.kwargs=kwargs
        for k,v in kwargs.items(): setattr(self,k,v)

    def selected(self, selectedData):
        if not selectedData: return {}
        
        points_data = selectedData.get('points',[])
        if not points_data: return {}

        def get_record_id(d, keys=['label', 'location']):
            if not d: return None
            for k in keys:
                if k in d:
                    return d[k]
            logger.exception('What is the record id here? --> '+pformat(d))
        
        selected_records = qualquant_series(
            [x for x in [ get_record_id(d) for d in points_data ] if x], 
            quant=self.quant
        ).sort_values().tolist()
        o={self.key:selected_records}
        return o
    

    @cached_property
    def dataset(self): 
        return (
            self.dataset_class.__func__() 
            if self.dataset_class is not None 
            else None
        )

    @cached_property
    def data_orig(self):
        return (
            self.dataset.data 
            if self.dataset is not None and self.dataset.data is not None
            else pd.DataFrame()
        )

    @cached_property
    def data_all(self):
        odf = self.data_orig
        # if self.drop_duplicates and len(odf):
        #     odf=odf.drop_duplicates(self.drop_duplicates)
        return odf
    
    @cached_property
    def total_counts(self):
        return self.dataset.data[self.key].value_counts()
    
    @cached_property
    def data(self):
        odf = filter_df(self.data_all, self.filter_data)
        if self.drop_duplicates and len(odf):
            odf=odf.drop_duplicates(self.drop_duplicates)
        return odf
    
    @cached_property
    def filter_desc(self):
        return filter_query_str(
            self.filter_data,
            human=True
        )
    
    def unique(
            self, 
            sort_by_count=True, 
            series_orig=True, 
            series_all=False,
            **kwargs): 
        l = list(self.get_series(**kwargs).unique())
        if not sort_by_count:
            l.sort(key=lambda x: x)
        else:
            if series_orig:
                # logger.debug('using original series')
                series = self.series_orig
            elif series_all:
                # logger.debug('using dedup\'d series')
                series = self.series_all
            else:
                # logger.debug('using dedup\'d and filtered')
                series = self.series
            counts = series.value_counts()
            l.sort(key=lambda x: -counts.loc[x])
        return pd.Series(l, name=self.key)



    @cached_property
    def series(self): return self.get_series(df=self.data)
    @cached_property
    def series_orig(self): 
        return self.get_series(df=self.data_orig)

    
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
        ).replace({'':UNKNOWN})
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
        return self.df_counts
    
    @cached_property
    def seldf(self) -> pd.DataFrame:
        if self.selection_data and len(self.figdf):
            return filter_df(self.figdf, self.selection_data)
        return pd.DataFrame()
    
    @cached_property
    def sels(self) -> list:
        return list(self.seldf.index) if len(self.seldf) else []
    
    @cached_property
    def seldata(self) -> dict:
        return {self.key:self.series.unique().tolist()}
    
    
    @cached_property
    def df_counts(self):
        valcounts = self.series.value_counts()
        if self.keep_missing_types:
            valtypes = self.series_all.unique()
            for missing_val in set(valtypes)-set(valcounts.index):
                valcounts[missing_val]=0
        return pd.DataFrame(valcounts).reset_index()

    @cached_property
    def fig(self): 
        logger.debug(f'{self.__class__.__name__}.fig')
        fig = self.plot()
        return fig
        

    def plot(self, **kwargs):
        kwargs={**self.kwargs, **kwargs}
        
        fig = self.plot_histogram(**kwargs)
        
        if self.sels:
            fig.update_traces(selectedpoints=self.sels)

        return fig
        
    def plot_histogram(self, color=None, **kwargs):
        color = color if color else self.color
        category_orders = (
            {self.key:self.df_counts.index} 
            if self.quant is False 
            else None
        )
        
        fig=px.bar(
            self.df_counts,
            x=self.key if not self.vertical else 'count',
            y='count' if not self.vertical else self.key, 
            height=self.height if not self.vertical else len(self.df_counts)*20,
            color_discrete_sequence=[color] if color else None,
            category_orders=category_orders,
            log_x=self.log_x,
            log_y=self.log_y,
            text=self.text,
            template=PLOTLY_TEMPLATE,
            hover_data={self.key:False, 'count':False},
            # **kwargs
        )
        fig.update_traces(textposition = 'auto', textfont_size=14)

        # cats=list(reversed(self.df_counts[self.key].index))        
        cats=list(self.df_counts[self.key].index)
        if self.vertical:
            fig.update_yaxes(categoryorder='array', categoryarray=cats, title_text='', tickangle=0, autorange='reversed')
            fig.update_xaxes(title_text=f'Number of {self.records_name}', visible=False)
        else:
            fig.update_xaxes(categoryorder='array', categoryarray=cats, title_text='')
            fig.update_yaxes(title_text=f'Number of {self.records_name}', visible=False)
        
        fig.update_layout(
            uniformtext_minsize=10,
            clickmode='event+select', 
            dragmode='select',
            selectdirection='h' if not self.vertical else 'v',
            margin={"r":0,"t":0,"l":0,"b":0},
        )
        if self.opts_xaxis: fig.update_xaxes(**self.opts_xaxis)
        if self.opts_yaxis: fig.update_yaxes(**self.opts_yaxis)

        return fig

class TypicalFigure(FigureFactory):
    height = 100
    # opts_xaxis=dict(title_text='')
    # opts_yaxis=dict(visible=False)

class MemberFigure(TypicalFigure):
    records_name='members'
    drop_duplicates=('member',)

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
    vertical = False
    text = 'count'
    
class NationalityFigure(FigureFactory):
    records_points_dim='y'
    vertical = True
    log_x = True
    text = 'count'


class MemberNationalityFigure(NationalityFigure, MemberFigure):
    records_name='member nationalities'
    key='member_nationalities'

class MemberArrondMap(MemberFigure):
    key='arrond_id'
    quant=False
    vertical = True
    text = 'count'

    @cached_property
    def df_counts(self):
        odf=super().df_counts
        series = odf[self.key]
        odf=odf[series.apply(is_valid_arrond)]
        odf['arrond_i'] = odf[self.key].apply(int)
        odf=odf.sort_values('arrond_i')
        odf.index = [x+1 for x in range(len(odf))]
        return odf
    
    def plot_map(self, color=None, height=250, **kwargs):
        kwargs={**self.kwargs, **kwargs}
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

class BookFigure(TypicalFigure):
    records_name='books'
    drop_duplicates=('book',)

class BookTitleFigure(BookFigure):
    key = 'book_title'

class BookGenreFigure(BookFigure):
    key = 'book_genre'
    vertical = True
    text = 'count'
    

class BookYearFigure(BookFigure):
    key = 'book_year'
    quant = True
    min_series_val=1800
    max_series_val=1950

class AuthorFigure(TypicalFigure):
    records_name='authors'
    drop_duplicates=('author',)

class AuthorGenderFigure(AuthorFigure):
    key='author_gender'
    quant=False
    vertical = False
    text='count'


class AuthorNationalityFigure(NationalityFigure, AuthorFigure):
    key='author_nationalities'
    quant=False

class AuthorDOBFigure(AuthorFigure):
    key = 'author_dob'
    quant = True
    min_series_val=1800
    max_series_val=1950

class MemberNameFigure(MemberFigure):
    key = 'member_name'
    drop_duplicates=('member',)

class AuthorNameFigure(MemberFigure):
    key = 'author_name'



class EventFigure(TypicalFigure):
    drop_duplicates = ('event',)

class EventYearFigure(EventFigure):
    key = 'event_year'
    quant = True

class EventMonthFigure(EventFigure):
    key = 'event_month'
    quant = True


class EventTypeFigure(EventFigure):
    key = 'event_type'
    quant = False
    vertical = True





### LANDMARKS

class LandmarksFigureFactory(FigureFactory):
    dataset_class = Landmarks
    # map_style = {
    #     "version": 8,
    #     "sources": {
    #         "raster-tiles": {
    #             "type": "raster",
    #             "tiles": ["http://localhost:5000/{z}/{x}/{y}.png"],
    #             "tileSize": 256
    #         }
    #     },
    #     "layers": [{
    #         "id": "simple-tiles",
    #         "type": "raster",
    #         "source": "raster-tiles",
    #         "minzoom": 0,
    #         "maxzoom": 18
    #     }]
    # }

    def plot_map(self, color='gray', **kwargs):
        figdf = self.data
        fig = go.Figure()
        fig.add_trace(
            go.Scattermapbox(
                below='',
                name='Landmarks',
                mode='markers+text',
                lat=figdf['lat'],
                lon=figdf['lon'],
                marker=go.scattermapbox.Marker(
                    color='black',
                    # symbol='square',
                    size=20,
                    # opacity=1
                    opacity=0.4
                ),
                text=figdf['landmark'],
                customdata=figdf['tooltip'],
                hovertemplate='%{customdata}<extra></extra>',
                textfont=dict(
                    size=TEXTFONT_SIZE,
                    family='Louize, Recursive, Tahoma, Verdana, Times New Roman',
                    color='black'
                ),
                textposition='bottom center',
                hoverlabel=dict(
                    font=dict(
                        size=16,
                        family='Louize, Recursive, Tahoma, Verdana, Times New Roman',
                        # color='black'
                    ),
                    bgcolor='white',
                ),
            )
        )

        # fig.update_layout(mapbox_style=self.map_style, mapbox_zoom=14)
        update_fig_mapbox_background(fig)
        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            legend=dict(
                yanchor="bottom",
                y=0.06,
                xanchor="right",
                x=0.99
            ),
            autosize=True
        )
        fig.layout._config = {'responsive':True, 'scrollZoom':True}
        fig.layout.update(showlegend=False)
        return fig
    
    def table(self, cols=[], sep=' ', **kwargs):
        return get_dash_table(self.data, cols=['landmark','address','arrond_id','lat','lon'])




def update_fig_mapbox_background(fig):
    fig.update_mapboxes(
        # style='mapbox://styles/ryanheuser/cljef7th1000801qu6018gbx8',
        # style='stamen-toner',
        style="streets",
        layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "https://warper.wmflabs.org/maps/6050",
                "source": [
                    "https://warper.wmflabs.org/maps/tile/6050/{z}/{x}/{y}.png"
                    # "/tiles/{z}/{x}/{y}.png"
                    # "http://127.0.0.1:5000/tiles/{z}/{x}/{y}.png"
                ],
                # "opacity":0.75
            }
        ],
        # style='mapbox://styles/ryanheuser/cllpenazf00ei01qi7c888uug',
        accesstoken=mapbox_access_token,
        bearing=0,
        center=MAP_CENTER,
        pitch=0,

        zoom=14,
    )
    return fig




### COMBINED?

class CombinedFigureFactory(FigureFactory):
    cols_table = ['member_name','memer_membership','member_dob','member_gender','member_nationalities','arrond_id']

    ## calcs
    @cached_property
    def arrond_counts(self): return self.valid_arronds.value_counts()
    @cached_property
    def arrond_percs(self):
        s=self.arrond_counts
        return (s/s.sum()) * 100
    
    @cached_property
    def df_dwellings(self): 
        assert 'dwelling' in set(self.data.columns)
        #o=self.data.drop_duplicates('dwelling').set_index('dwelling')
        bookcount={
            member_dwelling:len(set(member_dwelling_df.book))
            for member_dwelling,member_dwelling_df in self.data.groupby('dwelling')
        }
        def reversename(x):
            if not ',' in x: return x
            a,b=x.split(', ',1)
            return f'{b} {a}'
        return self.data.assign(
            num_borrows=[
                bookcount.get(x,0) for x in self.data.dwelling
            ],
            member_name_nice=self.data.member_name.apply(reversename),
            member_url=self.data.member.apply(lambda x: f'https://shakespeareandco.princeton.edu/members/{x}/')
        )
    
    @cached_property
    def df_members(self): 
        return self.data.drop_duplicates('member').set_index('member')
    
    def table_members(self, cols=[], sep=' ', **kwargs):
        return get_dash_table(self.df_members.reset_index(), cols=self.cols_table)
    
    @cached_property
    def book_filters_exist(self):
        return any(
            fn.startswith('book_') or fn.startswith('author_') or fn.startswith('event_') or fn.startswith('author_')
            for fn in self.filter_data
        )

    def table(self, cols=[], sep=' ', **kwargs):
        df = self.df_dwellings.reset_index()
        df=df[df.dwelling_address!='']
        
        # if only members filtered...
        if not self.book_filters_exist:
            df = df.drop_duplicates('dwelling')
            cols = cols_members
        else:
            df = df.drop_duplicates(['dwelling','book'])
            cols = cols_members+cols_books


        return get_dash_table(df, cols=cols)

        # df = (
        #     df.drop_duplicates('member') 
        #     if not self.book_filters_exist 
        #     else df.drop_duplicates(['dwelling','book'])
        # )
        # return get_dash_table(
        #     df,
        #     cols=(
        #         cols_members 
        #         if not self.book_filters_exist 
        #         else cols_members+cols_books
        #     )
        # )

    
    @cached_property
    def arronds(self):return qualquant_series(self.df_dwellings.arrond_id, quant=False)
    @cached_property
    def valid_arronds(self): 
        return self.arronds.loc[lambda v: v.str.isdigit() & (v!='99')]

    def plot_map(self, color=None, color_text='black', basefig=None, return_trace=False, **kwargs):
        if not color and self.color: color=self.color
        if not color: color=DEFAULT_COLOR
        figdf = self.df_dwellings.reset_index().fillna('').query('(lat!="") & (lon!="")')
        # figdf['hovertext']=[x[:100] for x in figdf['hover_tooltip']]

        trace = go.Scattermapbox(
            name=f'Member dwelling ({self.name})',
            mode='markers+text',
            lat=figdf['lat'],
            lon=figdf['lon'],
            customdata=figdf['hover_tooltip'],
            hovertemplate='%{customdata}<extra></extra>',
            marker=go.scattermapbox.Marker(
                color=color,
                symbol='circle',
                size=20,
                # size=(figdf['num_borrows'] / 20)+5,
                opacity=0.4
            ),
            text=figdf['member_name_nice'],
            textfont=dict(
                size=TEXTFONT_SIZE,
                color=color_text,
                family='Louize, Recursive, Tahoma, Verdana, Times New Roman'
            ),
            hoverlabel=dict(
                font=dict(
                    size=16,
                    family='Louize, Recursive, Tahoma, Verdana, Times New Roman',
                    # color='black'
                ),
                bgcolor='white',
            ),
            textposition='bottom center',
        )

        if return_trace: return trace


        fig = go.Figure()
        fig.add_trace(trace)
        return fig
        # basefig = LandmarksFigureFactory().plot_map() if basefig is None else basefig
        # return go.Figure(data=fig.data, layout=basefig.layout)




class ComparisonFigureFactory(CombinedFigureFactory):
    cols_table = ['L_or_R','member_name','memer_membership','member_dob','member_gender','member_nationalities','arrond_id']
    indiv_ff = CombinedFigureFactory

    def __init__(self, ff1={}, ff2={}, **kwargs):
        super().__init__(**kwargs)

        if is_listy(ff1) and not ff2 and len(ff1)==2:
            ff1,ff2 = ff1

        self.ff1 = self.L = self.indiv_ff(ff1,name='Filter 1') if type(ff1) in {dict,str} else ff1
        self.ff2 = self.R = self.indiv_ff(ff2,name='Filter 2') if type(ff2) in {dict,str} else ff2

    @cached_property
    def arrond_dists(self):
        return measure_dists(self.ff1.arrond_percs, self.ff2.arrond_percs)
    
    @cached_property
    def df_arronds(self): 
        return analyze_contingency_tables(
            self.L.valid_arronds,
            self.R.valid_arronds,
        )
    
    
    @cache
    def compare(self, 
            maxcats=COMPARISON_MAXCATS,
            cols=PREDICT_COLS,
            only_signif=False,
            round=4,
            min_count=PREDICT_MIN_COUNT,
            min_sum=PREDICT_MIN_SUM,
            **kwargs):
        
        return get_distinctive_qual_vals(
            self.L.df,
            self.R.df,
            maxcats=maxcats,
            cols=cols,
            only_signif=only_signif,
            round=round,
            min_count=min_count,
            min_sum=min_sum,
            drop_duplicates={
                'member':['member'],
                'author':['author','event'],
                'book':['book','event'],
                'arrond_id':['arrond_id','member']
            }
        )
    
    def describe_comparison(self, comparison_df=None, **kwargs):
        return describe_comparison(
            comparison_df
            if comparison_df is not None
            else self.compare(**kwargs)
        )

        
        
        

    
    @cached_property
    def df_dwellings(self): 
        # return combine_LR_df(
        #     self.ff1.df_dwellings, 
        #     self.ff2.df_dwellings
        # )
        return combine_LR_df(
            self.L.df_dwellings,
            self.R.df_dwellings, 
            colval_L='Filter 1',
            colval_R='Filter 2',
            colval_LR='Both Groups'
        )

    
    @cached_property
    def df_members(self): 
        return combine_LR_df(self.L.df_members, self.R.df_members)
        # return combine_LR_df(self.L.df_members, self.R.df_members)
    

    def plot_map(self, choro=False, **kwargs):
        
        # prepare data
        figdf = self.df_arronds.reset_index()
        def hover(row):
            if row.arrond_id and row.arrond_id.isdigit():
                return describe_arronds_row(row)
            else:
                return ''
        figdf = self.df_arronds.reset_index()
        figdf['hover']=figdf.apply(hover,axis=1)



        
        if choro:
            from colour import Color
            Lcolor = Color(LEFT_COLOR)
            Rcolor = Color(RIGHT_COLOR)
            midpoint = list(Lcolor.range_to(Rcolor, 3))[1]
            midpoint.set_luminance(.95)

            fig_choro = px.choropleth_mapbox(
                figdf,
                geojson=get_geojson_arrondissement(),
                locations='arrond_id', 
                color='perc_L->R',
                center=MAP_CENTER,
                zoom=14,
                hover_data=[],
                color_continuous_scale=[
                    Lcolor.hex,
                    midpoint.hex,
                    Rcolor.hex,
                ],
                opacity=.5,
            )
            customdata=np.stack((figdf['hover'],), axis=-1)
            fig_choro.update_traces(
                customdata=customdata,
                hovertemplate="%{customdata[0]}"
            )
            fig_choro.update_mapboxes(
                style='light',
                layers=[
                    {
                        "below":"traces",
                        "sourcetype": "raster",
                        "sourceattribution": "https://warper.wmflabs.org/maps/6050",
                        "source": [
                            "https://warper.wmflabs.org/maps/tile/6050/{z}/{x}/{y}.png"
                        ],
                        "opacity":0.25
                    }
                ]
            )
            
            ofig = fig_choro
        else:
            fig1=self.L.plot_map(color=LEFT_COLOR)
            fig2=self.R.plot_map(basefig=fig1, color=RIGHT_COLOR)
            ofig = go.Figure(
                data = fig1.data + fig2.data[0:1],
                layout=fig1.layout
            )

        ofig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            legend=dict(
                yanchor="bottom",
                y=0.06,
                xanchor="right",
                x=0.99
            ),
            coloraxis=dict(
                colorbar=dict(
                    orientation='h', 
                    y=.01,
                    lenmode='fraction',
                    len=.5,
                    thickness=10,
                    xanchor='right',
                    x=.99
                )
            )
        )
        return ofig

        

        def get_choro():
            from colour import Color

            Lcolor = Color(LEFT_COLOR)
            Rcolor = Color(RIGHT_COLOR)
            midpoint = list(Lcolor.range_to(Rcolor, 3))[1]
            midpoint.set_luminance(.95)

            def hover(row):
                if row.arrond_id and row.arrond_id.isdigit():
                    return describe_arronds_row(row)
                else:
                    return ''

            figdf = self.df_arronds.reset_index()
            figdf['hover']=figdf.apply(hover,axis=1)
            fig_choro = px.choropleth_mapbox(
                figdf,
                geojson=get_geojson_arrondissement(),
                locations='arrond_id', 
                color='perc_L->R',
                center=MAP_CENTER,
                zoom=12,
                # color_continuous_scale='puor',
                # hover_data = list(figdf.columns),
                hover_data=[],
                color_continuous_scale=[
                    LEFT_COLOR, 
                    # 'rgba(255,255,255,1)', 
                    # BOTH_COLOR,
                    midpoint.hex,
                    RIGHT_COLOR
                ],
                opacity=.5,
                # height=height,
                # template=PLOTLY_TEMPLATE
            )
            fig_choro.update_mapboxes(
                style='light',
                layers=[
                    {
                        "below": 'traces',
                        "sourcetype": "raster",
                        "sourceattribution": "https://warper.wmflabs.org/maps/6050",
                        "source": [
                            "https://warper.wmflabs.org/maps/tile/6050/{z}/{x}/{y}.png"
                        ]
                    }
                ]
            )
            customdata=np.stack((figdf['hover'],), axis=-1)
            fig_choro.update_traces(
                customdata=customdata,
                hovertemplate="%{customdata[0]}"
            )
            
            fig_choro.update_layout(
                margin={"r":0,"t":0,"l":0,"b":0},
                legend=dict(
                    yanchor="bottom",
                    y=0.06,
                    xanchor="right",
                    x=0.99
                )
            )
            fig_choro.update_layout(
                coloraxis=dict(
                    colorbar=dict(
                        orientation='h', 
                        y=.01,
                        lenmode='fraction',
                        len=.5,
                        thickness=10,
                        xanchor='right',
                        x=.99
                    )
                ),

            )
            return fig_choro

        # generate figs
        with Logwatch('generating scatter plot'):
            fig_scatter = get_scatter()

        with Logwatch('generating choropleth'):
            fig_choro = get_choro()

        with Logwatch('combining figs'):
            ofig=go.Figure(
                data=fig_choro.data + fig_scatter.data, 
                layout=fig_choro.layout
            )

        # final responsive layout patch
        ofig.update_layout(autosize=True)
        ofig.layout._config = {'responsive':True}
        return ofig
    
    def table_members(self, cols=[], sep=' ', **kwargs):
        return get_dash_table(self.df_members.reset_index(), cols=self.cols_table)
    
    def table_arrond(self, cols=[], **kwargs):
        # cols = ['arrond_id', 'count_L', 'count_R', 'perc_L', 'perc_R', 'perc_L->R']
        return get_dash_table(self.df_arronds.reset_index())
    
    def table_diff(self, cols=[], **kwargs):
        odf=self.rank_diff().query('rank_diff!=0')
        cols = ['rank_diff','group1_desc','group2_desc'] + [c for c in odf if c.endswith('_p')]
        return get_dash_table(odf,cols)
    
    def desc_table_diff(self, **kwargs):
        df=self.rank_diff()
        dfq=df[df.is_self==1]
        if not len(dfq): return ''

        row=dfq.iloc[0]
        n1,n2=self.diffkeys()
        return f'??'#Statistically, the spatial difference (difference in distribution across arrondissement) of the members is the ***{ordinal_str(row.rank_diff)}*** largest noted thus far. It ***{"is" if row.pvalue<=0.05 else "is not"}*** statistically significant, with a pvalue of ***{row.pvalue:.02}*** and a Mann-Whitney U test statistic of ***{row.statistic}***.'
            

            
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
                from scipy.stats import kstest, mannwhitneyu, pearsonr
                statd={}
                lvals = self.df_arronds.count_L.fillna(0)
                rvals = self.df_arronds.count_R.fillna(0)

                for statname,statf in [('kstest',kstest), ('mannwhitneyu',mannwhitneyu), ('pearsonr',pearsonr)]:
                    stat = statf(lvals,rvals)
                    statd[statname]=stat.statistic
                    statd[statname+'_p']=stat.pvalue
                cache[key]=statd
                cache.commit()
            return cache[key]


    def get_diffs(self):
        ld=[]
        with self.diffdb() as cache: 
            for key,val in cache.items():
                k1,k2=json.loads(key)
                ld.append(
                    dict(
                    group1=k1, 
                    group2=k2, 
                    group1_desc=format_intension(json.loads(k1)), 
                    group2_desc=format_intension(json.loads(k2)), 
                    **{kx:(float(kv) if is_numeric_dtype(kv) else kv) for kx,kv in dict(val).items()}))
        df=pd.DataFrame(ld)#.set_index(['group1','group2'])
        if len(df): df['is_self']=[((k1,k2) == self.diffkeys()) for k1,k2 in zip(df.group1, df.group2)]
        return df
        
        

    def rank_diff(self):
        self.measure_diff()
        df = self.get_diffs()
        if not len(df): return df
        pcols=[c for c in df if c.endswith('_p')]
        df['median_p'] = df[pcols].median(axis=1)
        df['rank_diff'] = df['median_p'].rank(ascending=True, method='first').apply(force_int)
        return df







def combine_figs(fig_new, fig_old):
    fig_old = go.Figure(fig_old) if type(fig_old)!=go.Figure else fig_old
    return go.Figure(
        layout=fig_old.layout if fig_old is not None and hasattr(fig_old,'data') and fig_old.data else fig_new.layout,
        data=fig_new.data
    )


def get_dash_table(df, cols=[], page_size=5, height_table='80vh', height_cell=60):
    cols=list(df.columns) if not cols else [col for col in cols if col in set(df.columns)]
    dff = delist_df(df[cols])
    cols_l = [{'id':col, 'name':col.replace('_',' ').title()} for col in cols]
    return dash_table.DataTable(
        data=dff.to_dict('records'),
        columns=cols_l,
        sort_action="native",
        sort_mode="multi",
        filter_action="native",
        page_action="native",
        # page_action="none",
        export_format='csv',
        page_size=page_size,
        fixed_rows={'headers': True},
        style_cell={
            'minWidth': 95, 'maxWidth': 95, 'width': 95,
        },

        style_data={
            'minHeight': height_cell, 'maxHeight': height_cell, 'height': height_cell,
            'whiteSpace': 'normal',
        },
        style_table={
            'height':400, 
            'overflowY':'auto',
            # 'display':'block',
            # 'flex-didrection':'column',
            # 'flex-grow':1,
            # 'width':'100%',
            # 'border':'1px solid #eeeee'
            # 'padding-bottom':'100px'
        },
    )



def get_empty_fig(height=100, width=250, **layout_kwargs):
    fig=go.Figure(layout=dict(height=height, width=width, **layout_kwargs))
    fig.update_layout(showlegend=False, template='simple_white')
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def get_color(x):
    if x=='L' or 'Left' in x: return LEFT_COLOR
    if x=='R' or 'Right' in x: return RIGHT_COLOR
    return BOTH_COLOR










# @cache
@cache_obj.memoize()
def ff_cache(figure_class, serialized_data):
    logger.debug(f'ff_cache({figure_class.__name__}, {serialized_data})')
    filter_data,selected,kwargs = unserialize(serialized_data)
    return figure_class(filter_data, selected, **kwargs)


# @cache
@cache_obj.memoize()
def plot_cache(figure_class, serialized_data):
    logger.debug(f'plot_cache({figure_class.__name__}, {serialized_data})')
    filter_data,existing_fig,kwargs = (
        unserialize(serialized_data) 
        if serialized_data 
        else ({},None,{})
    )
    ff = figure_class(filter_data)
    fig = ff.plot(**kwargs)
    if existing_fig: 
        fig = combine_figs(fig, existing_fig)
    return fig

