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
        ], className='layout-leftcol', width=5)
        
        right_col = dbc.Col(
            self.panels.layout_content(params), 
            className='layout-rightcol', 
            width=7
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
            dbc.Row(self.graphtab, className='content-belowtabs-row'),
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
        map_tabs = get_tabs([
            dict(label='Left vs. Right Groups', tab_id='map_LR'),
            dict(label='Left Group', tab_id='map_L'),
            dict(label='Right', tab_id='map_R'),
        ], tab_level=2, className='graphtabs-container')
        
        tbl_tabs = get_tabs(
            children=[
                dict(label='By member', tab_id='tbl_members'),
                dict(label='By arrond.', tab_id='tbl_arrond'),
                
            ], 
            tab_level=2, className='graphtabs-container'
        )

        analyze_tabs = get_tabs(
            children=[
                dict(
                    label='Magnitude of difference',
                    tab_id='tbl_diff'),                
            ], 
            tab_level=2, 
            className='graphtabs-container'
        )

        graphtabs = get_tabs(
            children=[
                dict(children=map_tabs, label='Map data', tab_id='map'),
                dict(children=tbl_tabs, label='View data', tab_id='tbl'),
                dict(children=analyze_tabs, label='Analyze data', tab_id='analyze')
            ], 
            tab_level=1, 
            className='graphtabs-container',
            active_tab='tbl'
        )
        return dbc.Container(graphtabs, className='graphtabs-container-container')
    
    @cached_property
    def graphtab(self):
        return dbc.Container(
            children=[html.Pre('Loading...')],
            className='graphtab-div'
        )




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
            Output(self.graphtab, 'children'),
            [
                Input(self.L.store, 'data'), 
                Input(self.R.store, 'data'),
                Input({"type": "tab_level_1", "index": ALL}, "active_tab"),
                Input({"type": "tab_level_2", "index": ALL}, "active_tab"),
                # Input(self.graphtabs, 'active_tab'),

            ]
        )
        def redraw_map(filter_data_L, filter_data_R, tab_ids_1, tab_ids_2):
            print(f'Tab ID 1: {tab_ids_1}')
            print()
            print(f'Tab ID 2: {tab_ids_2}')
            
            ff = fig = ComparisonMemberMap(filter_data_L, filter_data_R)
            self.comparison_map_fig = ff

            tab_ids_1_set=set(tab_ids_1)
            tab_ids_2_set=set(tab_ids_2)

            if 'tbl' in tab_ids_1_set:
                if 'tbl_members' in tab_ids_2_set:
                    return dbc.Container(
                        [
                            html.H4('Data by members'), 
                            html.P('Lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description '),
                            fig.table()
                        ], 
                        className='graphtab padded', 
                    )
                elif 'tbl_arrond' in tab_ids_2_set:
                    return dbc.Container(
                        [
                            html.H4('Data by arrondissement'), 
                            fig.table_arrond()
                        ], 
                        className='graphtab padded', 
                    )
            elif 'analyze' in tab_ids_1_set:
                if 'tbl_diff' in tab_ids_2_set:
                    return dbc.Container(
                        [
                            html.H4('Degree of difference compared'),
                            html.P(
                                dcc.Markdown(
                                    fig.desc_table_diff()
                                )
                            ), 
                            fig.table_diff()
                        ], 
                        className='graphtab padded', 
                    )
            elif 'map' in tab_ids_1_set:
                ofig = ff.plot()
                ofig.update_layout(autosize=True)
                ograph = dcc.Graph(
                    figure=ofig, 
                    className='comparison_map_graph'
                )
                return [dbc.Container(ograph, className='graphtab')]




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


