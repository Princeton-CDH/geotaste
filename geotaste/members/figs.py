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
            # height=250,
            size_max=40,
            template=PLOTLY_TEMPLATE
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
            opacity=.5,
            # height=250,
            template=PLOTLY_TEMPLATE
        )
        fig_choro.update_mapboxes(style="stamen-toner")
        fig_choro.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            clickmode='event+select', 
        )
        fig_choro.update_traces(marker_line_width=2)
        ofig=go.Figure(data=fig_choro.data + fig.data, layout=fig_choro.layout)
        ofig.update_layout(autosize=True)
        ofig.layout._config = {'responsive':True}
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
            color_continuous_scale='puor',
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
        
        fig_choro.update_coloraxes(reversescale=True)
        ofig=go.Figure(
            data=fig_choro.data + fig.data, 
            layout=fig_choro.layout
        )
        ofig.update_layout(autosize=True)
        ofig.layout._config = {'responsive':True}
        return ofig



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

