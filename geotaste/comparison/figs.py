from ..imports import *
from ..combined.figs import CombinedFigureFactory



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
        dfL = self.L.df_dwellings.assign(L_or_R='L')
        dfR = self.R.df_dwellings.assign(L_or_R='R')
        return pd.concat([dfL,dfR])
    
    @cached_property
    def df_members(self): 
        return combine_LR_df(self.L.df_members, self.R.df_members)
    

    def plot(self, height=250, **kwargs):
        def get_color(x):
            if x.startswith('L'): return LEFT_COLOR
            if x.startswith('R'): return RIGHT_COLOR
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
        return get_dash_table(self.df_members.reset_index())
    
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






