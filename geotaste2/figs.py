from .imports import *


###########
# Figures #
###########

class FigureFactory(DashFigureFactory, Logmaker):
    records_name = 'records'
    key = ''
    records_points_dim = 'xy'
    dataset_class = CombinedDataset
    drop_duplicates = ()
    quant = False
    opts_xaxis=dict()
    opts_yaxis=dict()
    height=600
    color=None
    min_series_val=None
    max_series_val=None
    
    def __init__(self, filter_data={}, **kwargs):
        if filter_data is None: filter_data = {}
        self.filter_data = filter_data

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
        logger.debug(f'selected: {selected_records}')
        return {self.key:selected_records}
    

    @cached_property
    def dataset(self): 
        return (self.dataset_class() if self.dataset_class is not None else None)

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
    
    @property
    def filter_desc(self):
        return format_intension(self.filter_data.get(INTENSION_KEY,{}))
    
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
            # **kwargs
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
    
class NationalityFigure(FigureFactory):
    records_points_dim='y'

    def plot(self, color=None, **kwargs):
        df_counts = make_counts_df(self.series)        
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
        fig.update_xaxes(title_text=f'Number of {self.records_name}', visible=False)
        fig.update_yaxes(title_text='', tickangle=0, autorange='reversed')
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return fig

class MemberNationalityFigure(NationalityFigure, MemberFigure):
    records_name='member nationalities'
    key='member_nationalities'

class MemberArrondMap(MemberFigure):
    key='arrond_id'
    
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

class BookFigure(TypicalFigure):
    records_name='books'
    drop_duplicates=('book',)

class BookTitleFigure(BookFigure):
    key = 'book_title'

class BookYearFigure(BookFigure):
    key = 'book_year'
    quant = True
    min_series_val=1800
    max_series_val=1950

class CreatorFigure(TypicalFigure):
    records_name='creators'
    drop_duplicates=('creator',)

class CreatorGenderFigure(CreatorFigure):
    key='creator_gender'
    quant=False

class CreatorNationalityFigure(NationalityFigure, CreatorFigure):
    key='creator_nationalities'
    quant=False

class CreatorDOBFigure(CreatorFigure):
    key = 'creator_dob'
    quant = True
    min_series_val=1800
    max_series_val=1950

class MemberNameFigure(MemberFigure):
    key = 'member_name'

class CreatorNameFigure(MemberFigure):
    key = 'creator_name'









### COMBINED?

class CombinedFigureFactory(FigureFactory):
    pass
    # ## calcs
    # @cached_property
    # def arrond_counts(self): 
    #     # return get_arrond_counts_series(self.valid_arronds)
    #     return self.valid_arronds.value_counts()
    # @cached_property
    # def arrond_percs(self):
    #     s=self.arrond_counts
    #     return (s/s.sum()) * 100
    # @cached_property
    # def arronds(self):return self.df_dwellings.arrond_id
    # @cached_property
    # def valid_arronds(self): return self.arronds.loc[lambda v: v.str.isdigit() & (v!='99')]















class ComparisonFigureFactory(FigureFactory):
    cols_table = ['name','membership_years','birth_year','gender','nationalities','arrond_id','L_or_R']
    indiv_ff = CombinedFigureFactory

    def __init__(self, ff1={}, ff2={}, **kwargs):
        super().__init__(**kwargs)

        if is_listy(ff1) and not ff2 and len(ff1)==2:
            ff1,ff2 = ff1

        self.ff1 = self.L = self.indiv_ff(ff1) if type(ff1)==dict else ff1
        self.ff2 = self.R = self.indiv_ff(ff2) if type(ff2)==dict else ff2

    @cached_property
    def arrond_dists(self):
        return measure_dists(self.ff1.arrond_percs, self.ff2.arrond_percs)
    
    @cached_property
    def df_arronds(self): 
        return analyze_contingency_tables(
            self.L.valid_arronds,
            self.R.valid_arronds,
        )
    
    @cached_property
    def signif_arronds(self):
        return filter_signif(self.df_arronds)
    
    @cached_property
    def df_dwellings(self): 
        return combine_LR_df(
            self.L.df_dwellings, 
            self.R.df_dwellings
        )

    
    @cached_property
    def df_members(self): 
        return combine_LR_df(self.L.df_members, self.R.df_members)
    

    def plot(self, height=250, **kwargs):
        def get_color(x):
            if x=='L': return LEFT_COLOR
            if x=='R': return RIGHT_COLOR
            return BOTH_COLOR
        
        df = self.df_dwellings
        color_map = {label:get_color(label) for label in df['L_or_R'].apply(str).unique()}
        fig = px.scatter_mapbox(
            df, 
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
