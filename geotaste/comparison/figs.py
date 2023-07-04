from ..imports import *


class ComparisonFigureFactory(FigureFactory):
    dataset_class = MembersDataset
    
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
            EXTENSION_KEY:{i:{} for i in self.dataset.data.index}
        }

    @cached_property
    def df_L(self): 
        return self.df[self.df.L_or_R.isin({'L','Both'})]
    
    @cached_property
    def df_R(self): 
        return self.df[self.df.L_or_R.isin({'R','Both'})]
    
    @cached_property
    def df_arronds(self): 
        return compare_arrond_counts(self.df_L, self.df_R)

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
        return get_dash_table(self.df_arronds, cols=cols)
    
    def table_diff(self, cols=[], **kwargs):
        return get_dash_table(self.rank_diff(), cols=['rank_diff', 'group1', 'group2', 'pvalue', 'statistic', 'is_self'])
    
    def desc_table_diff(self, **kwargs):
        df=self.rank_diff()
        dfq=df[df.is_self==1]
        print(dfq)
        if not len(dfq): return ''

        row=dfq.iloc[0]
        n1,n2=self.diffkeys()
        return f'Statistically, the spatial difference (difference in distribution across arrondissement) of the members is the ***{ordinal_str(row.rank_diff)}*** largest noted thus far. It ***{"is" if row.pvalue<=0.05 else "is not"}*** statistically significant, with a pvalue of ***{row.pvalue:.02}*** and a Kolmogorov–Smirnov test statistic of ***{row.statistic:.02}***.'
            

            
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
        df['rank_diff'] = df.statistic.rank(ascending=False, method='first').astype(int)
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

