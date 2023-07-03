from ..imports import *
from .components import *
from ..members.components import *
from ..books.components import *

STYLE_INVIS={'display':'none'}
STYLE_VIS={'display':'flex'}


# STYLE_INVIS={'visibility':'hidden'}
# STYLE_VIS={'visibility':'visible'}

# STYLE_INVIS = {'position': 'absolute', 'top': '-9999px', 'left': '-9999px'}
# STYLE_VIS = {'position': 'relative'}

class GeotasteLayout(BaseComponent):
    def __init__(self):
        super().__init__(title="Geography of Taste")
        self.panels = PanelComparison()
        # self.ticker = dcc.Interval(interval=1*1000, n_intervals=0)
        self.last_window_size = None


    @cached_property
    def logo(self):
        return html.Div([
            html.Img(src=LOGO_SRC, className='logo-img'),
            html.H1(self.title, className='logo-title'),
            # html.Img(src=LOGO_SRC, className='logo-img'),
        ], className='logo')

    @cached_property
    def navbar(self):
        return dbc.Row([
            dbc.Col(self.logo, className='logo-col', width=4),
            dbc.Col(self.panels.toptabs, className='toptabs-col', width=8)
        ], className='navbar-row')



    @cached_property
    def content(self):
        return dbc.Row(self.panel_comparison.layout())

    def layout(self, params=None):
        top_row = dbc.Row(self.panels.layout_top(params), className='layout-toprow')
        main_row = dbc.Row(self.panels.layout_main(params), className='layout-mainrow')
        
        left_col = dbc.Col([
            top_row, 
            main_row
        ], className='layout-leftcol', width=6)
        
        right_col = dbc.Col(
            self.panels.layout_content(params), 
            className='layout-rightcol', 
            width=6
        )

        notnavbar = dbc.Row([left_col, right_col], className='layout-belownavbar')

        return dbc.Container([self.navbar, notnavbar], className='layout-container')




class PanelComparison(BaseComponent):
    def __init__(self, *x, **y):
        super().__init__(*x,**y)
        self.L = LeftPanel()
        self.R = RightPanel()

    @cached_property
    def comparison_map_graph(self):
        return dcc.Graph(
            figure=go.Figure(), 
            className='comparison_map_graph'
        )
    
    @cached_property
    def comparison_map_graph_div(self):
        return html.Div(self.comparison_map_graph)
    
    @cached_property
    def comparison_map_table(self):
        return html.Div(
            html.Pre('Table placeholder'), 
            className='comparison_map_table'
        )
    
    @cached_property
    def dueling_maps_row(self, params=None):
        return dbc.Row([
            dbc.Col(self.L.map_graph, width=6),
            dbc.Col(self.R.map_graph, width=6),
        ], className='bimap-row')
    
    @cached_property
    def dueling_descs_row(self, params=None):
        return dbc.Row([
            dbc.Col(
                html.H2([
                    'Left Group: ', 
                    self.L.store_desc
                ]), 
                width=6, 
                className='storedescs-col storedescs-col-L left-color'
            ),
            dbc.Col(
                html.H2([
                    'Right Group: ', 
                    self.R.store_desc
                ]),
                width=6, 
                className='storedescs-col storedescs-col-R right-color'
            ),
        ], className='storedescs-row')
        
    def layout_top(self, params=None):
        return dbc.Container([
            self.dueling_descs_row,
            # self.toptabs       # -> this now moved up to navbar level in GeotasteLayout
        ])
    
    def layout_main(self, params=None):
        return dbc.Container([
            self.layout_dueling_panels(params)
        ])
    
    def layout_content(self, params=None):
        return dbc.Container([
            dbc.Row(self.graphtabs, className='content-tabs-row'),
            dbc.Row(self.comparison_map_graph_div, className='content-map-row comparemap-row'),
            dbc.Row(self.comparison_map_table, className='content-table-row')
        ], className='layout-content-container')
    
    def layout_dueling_panels(self, params=None):
        return dbc.Row([
            dbc.Col(self.L.layout(params), width=6, className='panel_L panel'),
            dbc.Col(self.R.layout(params), width=6, className='panel_R panel'),
        ])
    

    @cached_property
    def toptabs(self):
        return dbc.Tabs([
            dbc.Tab(label='Where did members live?', tab_id='members'),
            dbc.Tab(label='Which books were borrowed?', tab_id='books'),
            # dbc.Tab(label='Borrowing event', tab_id='events'),
        ], className='navtabs-container', active_tab='members')
    
    @cached_property
    def graphtabs(self):
        return dbc.Tabs([
            dbc.Tab(label='Map', tab_id='map'),
            dbc.Tab(label='Data', tab_id='table'),
        ], className='graphtabs-container', active_tab='table')
    




    def component_callbacks(self, app):
        super().component_callbacks(app)

        @app.callback(
            output=[
                (
                    Output(self.L.member_panel_row, 'style'),
                    Output(self.R.member_panel_row, 'style'),
                ),
                (
                    Output(self.L.book_panel_row, 'style'),
                    Output(self.R.book_panel_row, 'style'),
                )
            ],
            inputs=[Input(self.toptabs, 'active_tab')]
        )
        def switch_toptabs(tab_id, num_tabs=2):
            invis=tuple([STYLE_INVIS for n in range(num_tabs)])
            vis=tuple([STYLE_VIS for n in range(num_tabs)])
            return (invis,vis) if tab_id=='books' else (vis,invis)
        
        @app.callback(
            [
                Output(self.comparison_map_graph_div, 'style'),
                Output(self.comparison_map_table, 'style'),
            ],
            [
                Input(self.graphtabs, 'active_tab')
            ]
        )
        def switch_graphtabs(tab_id, num_tabs=2):
            invis=tuple([STYLE_INVIS for n in range(num_tabs)])
            vis=tuple([STYLE_VIS for n in range(num_tabs)])
            return (STYLE_INVIS,STYLE_VIS) if tab_id=='table' else (STYLE_VIS,STYLE_INVIS)
        
        
        @app.callback(
            [
                Output(self.comparison_map_graph, 'figure'),
                Output(self.comparison_map_table, 'children'),
            ],
            [
                Input(self.L.store, 'data'), 
                Input(self.R.store, 'data')
            ],
            State(self.comparison_map_graph, 'figure'),
        )
        def redraw_map(filter_data_L, filter_data_R, old_figdata):
            fig = ComparisonMemberMap(filter_data_L, filter_data_R)
            self.comparison_map_fig = fig
            ofig = combine_figs(
                fig_new=fig.plot(),
                fig_old=old_figdata
            )
            tables = dbc.Container([
                dbc.Row([html.H4('Data by members'), fig.table()], className='h-20 align-top', style={'display':'block'}),
                dbc.Row([html.H4('Data by arrondissement'), fig.table_arrond()], className='h-20 align-top', style={'display':'block'}),
                dbc.Row([html.H4('Degree of difference compared'), fig.table_diff()], className='h-20 align-top', style={'display':'block'})
            ])
            return [ofig, tables]




class MemberBookEventPanel(FilterComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.member_panel = MemberPanel(**kwargs)
        self.book_panel = BookPanel(**kwargs)
        
        # defaults
        self.map_fig = self.map_ff()

    def layout(self, params=None):
        return dbc.Container([
            self.store,
            self.member_panel_row,
            self.book_panel_row
        ])
    
    @cached_property
    def member_panel_row(self, params=None):
        return dbc.Row(
            self.member_panel.layout(params), 
            className='member-panel', 
            id=dict(index=f'member-{self.L_or_R}', type='member-panel')
        )
    
    @cached_property
    def book_panel_row(self, params=None):
        return dbc.Row(
            self.book_panel.layout(params), 
            className='book-panel', 
            id=dict(index=f'book-{self.L_or_R}', type='book-panel')
        )
    
    def map_ff(self, filter_data={}):
        if not filter_data: filter_data=self.filter_data
        return MemberMap(filter_data)

    @cached_property
    def map_graph(self):
        return dcc.Graph(figure=self.map_fig.plot(**self._kwargs))

    def component_callbacks(self, app):
        super().component_callbacks(app)

        @app.callback(
            Output(self.store, 'data'),
            [ 
                Input(self.member_panel.store, 'data'),
                Input(self.book_panel.store, 'data'),
            ]
        )
        def component_filters_updated(*filters_d):
            self.filter_data = intersect_filters(*filters_d)
            return self.filter_data
        
        # @app.callback(
        #     Output(self.map_graph, 'figure'),
        #     Input(self.store, 'data'),
        #     State(self.map_graph, 'figure'),
        #     prevent_initial_call=True
        # )
        # def redraw_map(filter_data, fig_old):
        #     self.map_fig = self.map_ff(filter_data)
        #     fig_new = self.map_fig.plot(**self._kwargs)
        #     return combine_figs(fig_new,fig_old)

        


class LeftPanel(MemberBookEventPanel):
    def __init__(self, **kwargs):
        super().__init__(
            L_or_R='L', 
            color=LEFT_COLOR,
            **kwargs
        )
    
class RightPanel(MemberBookEventPanel):
    def __init__(self, **kwargs):
        super().__init__(
            L_or_R='R', 
            color=RIGHT_COLOR, 
            **kwargs
        )


