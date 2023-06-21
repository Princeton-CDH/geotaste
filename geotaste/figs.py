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
        if not x in set(df.columns): return go.Figure()
        s=df[x].value_counts()

        # make sure all types are there
        missing_valtypes = set(self.vals) - set(s.index)
        for xval in missing_valtypes: s[xval]=0
        s=s.sort_index()

        df_counts = pd.DataFrame(s).reset_index()

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
            color_continuous_scale='oranges' if color == RIGHT_COLOR else 'purples',
            range_color=(0,400), #fdf['count'].min(), fdf['count'].max())
            height=300,
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
    
class MemberTableFigure(MemberFigure, TableFigure):
    cols = ['name','title','gender','birth_year','death_year','nationalities']

    def plot(self, **kwargs):
        cols = self.cols if self.cols else self.df.columns
        dff = self.df[[c for c in cols if c in set(self.df.columns)]]
        for col in set(cols) & set(Members().cols_sep):
            dff[col] = dff[col].apply(lambda x: Members().sep.join(str(y) for y in x))
        return super().plot(df=dff)
    




class MemberMap(MemberFigure):
    def __init__(self, filter_data={}, df=None):
        super().__init__(
            df=MemberDwellings().data if df is None else df,
            filter_data=filter_data
        )

    def plot(self, color=None, **kwargs):
        fig = px.scatter_mapbox(
            self.df.reset_index(), 
            lat='latitude',
            lon='longitude', 
            center=dict(lat=LATLON_SCO[0], lon=LATLON_SCO[1]),
            custom_data=['member'],
            zoom=12, 
            hover_name='name',
            height=400,
            size_max=40,
        )
        fig.update_traces(marker=dict(size=10))
        if color: fig.update_traces(marker=dict(color=color))
        fig.update_mapboxes(style="stamen-toner")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        # counts_by_arrond = pd.DataFrame(self.df.arrond_id.value_counts()).reset_index()
        counts_by_arrond = get_arrond_counts(self.df).reset_index()

        fig_choro = px.choropleth_mapbox(
            counts_by_arrond,
            geojson=get_geojson_arrondissement(),
            locations='arrond_id', 
            color='count',
            center=MAP_CENTER,
            zoom=12,
            color_continuous_scale='oranges' if color == RIGHT_COLOR else 'purples',
            opacity=.5
        )
        fig_choro.update_mapboxes(style="stamen-toner")
        fig_choro.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            clickmode='event+select', 
        )
        fig_choro.update_traces(marker_line_width=2)
        ofig=go.Figure(data=fig_choro.data + fig.data, layout=fig_choro.layout)
        return ofig

    def selected(self, selectedData):
        if selectedData:
            print('selectedData',selectedData)
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

    def plot(self, **kwargs):
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
            # height=400,
            size_max=40,
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
            color_continuous_scale='puor',
            opacity=.5
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
                    y=-0.15)
                ),
        )
        fig_choro.update_coloraxes(reversescale=True)
        return go.Figure(data=fig_choro.data + fig.data, layout=fig_choro.layout)



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




## geojson/arrond utils

def get_geojson_arrondissement(force=False):
    import os,json,requests
    
    # download if nec
    url=URLS.get('geojson_arrond')
    fn=os.path.join(PATH_DATA,'arrondissements.geojson')
    if force or not os.path.exists(fn):
        data = requests.get(url)
        with open(fn,'wb') as of: 
            of.write(data.content)

    # load        
    with open(fn) as f:
        jsond=json.load(f)
        
    # anno
    for d in jsond['features']:
        d['id'] = str(d['properties']['c_ar'])
        d['properties']['arrond_id'] = d['id']
    
    return jsond


@cache
def get_all_arrond_ids():
    return {
        d['id'] 
        for d in get_geojson_arrondissement()['features']
    }

def get_arrond_counts(df,key='arrond_id'):
    arrond_counts = {n:0 for n in sorted(get_all_arrond_ids(), key=lambda x: int(x))}
    for k,v in dict(df[key].value_counts()).items(): arrond_counts[k]=v    
    arrond_df = pd.DataFrame([arrond_counts]).T.reset_index()
    arrond_df.columns=[key, 'count']
    arrond_df['perc']=arrond_df['count'] / sum(arrond_df['count']) * 100
    return arrond_df.set_index(key)

def compare_arrond_counts(df_L, df_R):
    df_arronds_L = get_arrond_counts(df_L)
    df_arronds_R = get_arrond_counts(df_R)
    df_arronds_diff = df_arronds_R - df_arronds_L
    odf=pd.DataFrame()
    for c in df_arronds_diff:
        odf[c+'_L']=df_arronds_L[c]
        odf[c+'_R']=df_arronds_R[c]
        odf[c+'_L->R']=df_arronds_diff[c]
    odf=odf.sort_values('perc_L->R')
    return odf