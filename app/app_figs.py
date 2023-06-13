from app_imports import *



##################################################
# COMPONENTS
##################################################


class FigureFactory(DashFigureFactory):
    def __init__(self, filter_data = {}, df = None):
        self.filter_data = filter_data
        self._df = df

    @cached_property
    def df(self):
        if self._df is None: return pd.DataFrame()
        return filter_df(self._df, self.filter_data)
    
    def plot_biplot(self, x_axis, y_axis, qual_col):
        return px.scatter(
            self.df,
            x=x_axis,
            y=y_axis,
            color=qual_col,
            template='plotly_dark',
            # trendline="ols",
            # trendline_color_override="orange",
            # trendline_scope='overall',
            # trendline_options=dict(frac=0.1)
            marginal_x='box',
            marginal_y='box'
        )
    
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
        
        print(color,'color???')
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
            **kwargs
        )
        if mapbox_style: mapbox_opts['style']=mapbox_style
        fig.update_layout(mapbox=mapbox_opts)
        # fig.update_traces(marker=dict(size=6, color='#811818'))
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        return fig
    


class MemberFigureFactory(FigureFactory):
    def __init__(self, filter_data={}): 
        super().__init__(
            df=Members().data,
            filter_data=filter_data
        )

    def plot_dob(self, color=None):
        fig=px.histogram(
            self.df, 
            'birth_year', 
            height=200, 
            color_discrete_sequence=[color] if color else None,
            template='simple_white'
            )
        fig.update_layout(
            clickmode='event+select', 
            dragmode='select', 
            selectdirection='h',
            margin={"r":0,"t":0,"l":0,"b":0},
        )
        return fig



class MemberDwellingsFigureFactory(FigureFactory):
    def __init__(self, filter_data={}, df=None):
        super().__init__(
            df=MemberDwellings().data if df is None else df,
            filter_data=filter_data
        )
    
    def plot_map(self, color=None, **kwargs):
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
        print(color_map)

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
    

