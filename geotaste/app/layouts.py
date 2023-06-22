from ..imports import *
from .components import *
from ..members.components import *
from ..books.components import *


class GeotasteLayout(BaseComponent):
    def __init__(self):
        super().__init__(title="Geography of Taste")
        self.panel_L = MemberPanel(color=LEFT_COLOR)
        self.panel_R = MemberPanel(color=RIGHT_COLOR)

    @cached_property
    def navbar(self):
        return dbc.Navbar([
            html.Img(src=LOGO_SRC, height="30px", className='logo-img'),
            dbc.NavbarBrand("Geography of Taste", className='logo-title'),
            # self.tabs
        ], color="light", dark=False)
    
    # @cached_property
    # def tabs(self, cn1='custom-tab', cn1s='custom-tab--selected', cn2='custom-tabs', cn2x='tabs-container'):
    #     return dcc.Tabs(
    #         [
    #             dcc.Tab(label='Juxtapose', value='juxtapose', className=cn1, selected_className=cn1s),
    #             dcc.Tab(label='Contrast', value='contrast', className=cn1, selected_className=cn1s),
    #         ], 
    #         className=cn2x, 
    #         value='juxtapose',
    #         parent_className=cn2
    #     )
    
    
    @cached_property
    def comparison_map_card(self): return MemberMapComparisonCard()
    
    def layout_content_toptabs(self, params=None): 
        return dbc.Container([
            dbc.Row([
                dbc.Tabs([
                    dbc.Tab(self.comparison_map_card.graph, label='Map'),
                    dbc.Tab(self.comparison_map_card.table, label='Table'),
                ])
            ], style={'marginLeft':'auto'}),
            dbc.Row([
                dbc.Col(self.panel_L.layout(params), width=6),
                dbc.Col(self.panel_R.layout(params), width=6),
            ])
        ])
    
    def layout_3row(self, params=None):
        return dbc.Container([
            dbc.Row([
                self.navbar,
                dbc.Row([
                    dbc.Col(self.panel_L.map_card.layout(params), width=6),
                    dbc.Col(self.panel_R.map_card.layout(params), width=6),
                ])
            ], className='layout-toprow'),

            dbc.Row([
                dbc.Row([
                    dbc.Col(self.panel_L.layout(params), width=6),
                    dbc.Col(self.panel_R.layout(params), width=6),
                ]),
                dbc.Row(self.comparison_map_card.table)
            ], className='layout-mainrow'),

            dbc.Row(self.comparison_map_card.graph, className='layout-bottomrow'),
        ], className='layout-container')
    
    def dual_map_row(self, params=None):
        return dbc.Row([
            dbc.Col(self.panel_L.map_card.layout(params), width=6),
            dbc.Col(self.panel_R.map_card.layout(params), width=6),
            # dbc.Col([self.panel_L.map_card.graph, self.panel_L.map_card.store], width=6),
            # dbc.Col([self.panel_R.map_card.graph, self.panel_R.map_card.store], width=6),
        ], className='bimap-row')
    
    def dual_panel_row(self, params=None):
        return dbc.Row([
            dbc.Col(self.panel_L.layout(params), width=6),
            dbc.Col(self.panel_R.layout(params), width=6),
        ])
    
    def dual_store_descs(self, params=None):
        return dbc.Row([
            dbc.Col(self.panel_L.store_desc, width=6),
            dbc.Col(self.panel_R.store_desc, width=6),
        ], className='storedescs-row')
    
    def toptabs(self, params=None, tab_cn='toprow-tab', tabs_cn='toprow-tabs'):
        tabs = dbc.Tabs(
            [
                dbc.Tab(
                    self.dual_map_row(params), 
                    label='Map juxtaposition',
                    className=tab_cn,
                    # selected_className=f'{tab_cn}--selected'
                ),
                dbc.Tab(
                    self.comparison_map_card.layout(params), 
                    label='Map contrast',
                    className=tab_cn,
                    # selected_className=f'{tab_cn}--selected'
                ),
                # dbc.Tab(
                #     self.comparison_map_card.table, 
                #     label='Table contrast',
                #     className=tab_cn,
                #     # selected_className=f'{tab_cn}--selected'
                # )
            ],
            # parent_className=tabs_cn
        )
        return dbc.Row(tabs, className='toptabs-row')
    
    def layout_toptabs(self, params=None):
        return dbc.Container([
            dbc.Row(dbc.Col([
                dbc.Row(self.navbar),
                self.toptabs(params),
                self.dual_store_descs(params),
            ]), className='layout-toprow', align='start'),

            dbc.Row(dbc.Col([
                self.dual_panel_row(params),
                dbc.Row(self.comparison_map_card.table),
            ]), className='layout-mainrow', align='start'),

        ], className='layout-container')
    
    def layout_tripletop(self, params=None):
        return dbc.Container([
            dbc.Row([
                self.navbar,
                self.comparison_map_card.graph,
                self.dual_map_row(params),
                self.dual_store_descs(params)
            ], className='layout-toprow'),

            dbc.Row([
                self.dual_panel_row(params),
                dbc.Row(self.comparison_map_card.table)
            ], className='layout-mainrow'),

        ], className='layout-container')
    

    layout = layout_toptabs





    def component_callbacks(self, app):
        @app.callback(
            [
                Output(self.comparison_map_card.graph, 'figure'),
                Output(self.comparison_map_card.table, 'children'),
            ],
            [
                Input(self.panel_L.store, 'data'), 
                Input(self.panel_R.store, 'data')
            ],
            State(self.comparison_map_card.graph, 'figure'),
        )
        def redraw_map(filter_data_L, filter_data_R, old_figdata):
            print('redraw_map')
            fig = ComparisonMemberMap(
                filter_data_L,
                filter_data_R
            )
            fig_new = fig.plot()
            fig_old = go.Figure(old_figdata)
            ofig = go.Figure(
                layout=fig_old.layout if fig_old.data else fig_new.layout,
                data=fig_new.data
            )

            # table
            # print(fig.df_arronds)
            table_fig = ComparisonMemberTable(
                df=round(fig.df_arronds,2).reset_index(),    
            )
            table_ofig = table_fig.plot()
            return [ofig, table_ofig]
    






class GeotasteTopmapLayout(GeotasteLayout):
    def __init__(self):
        super().__init__()
        self.navbar = Navbar()
        self.member_panel_L = MemberPanel(name='member_panel_L', color=LEFT_COLOR)
        self.member_panel_R = MemberPanel(name='member_panel_R', color=RIGHT_COLOR)

    def layout_content(self, params=None):
        return dbc.Container([
            dbc.
            
            dbc.Row([
                dbc.Col(
                    self.panel_L.layout(params),
                    width=6
                ),
                dbc.Col(
                    self.panel_R.layout(params),
                    width=6
                ),
            ], className='comparison_row'),
            
            
        ])
    
    

            
        

class MemberBookPanel(FilterComponent):
    def __init__(self, **kwargs):
        self.member_panel = MemberPanel(**kwargs)
        self.book_panel = BookPanel(**kwargs)
        self.map_panel = MemberMapCard(**kwargs)

    def layout(self, params=None):
        return dbc.Container([
            dbc.Row([
                dbc.Col(self.member_panel.layout(params)),
                dbc.Col(self.book_panel.layout(params)),
                dbc.Col(self.map_panel.layout(params)),
            ])
        ])
















class GeotasteTabLayout(GeotasteLayout):
    @cached_property
    def tabs(self):
        return dbc.Tabs([
            dbc.Tab(label='Group 1', tab_id='tab1'),
            dbc.Tab(label='Group 2', tab_id='tab2'),
            dbc.Tab(label='Compare', tab_id='tab3'), 
        ], className='tabs-container', active_tab='tab1')

    @cached_property
    def tab1_content(self):
        return html.Div(self.panel_L.layout(), style={'display':'none'})
    
    @cached_property
    def tab2_content(self):
        return html.Div(self.panel_R.layout(), style={'display':'none'})
    
    @cached_property
    def tab3_content(self):
        return html.Div('Comparison', style={'display':'none'})

    @cached_property
    def content(self):
        return dbc.Container([
            self.tabs,
            self.tab1_content,
            self.tab2_content,
            self.tab3_content,
        ], className='content-container')
    
    def component_callbacks(self, app):
        @app.callback(
            [
                Output(self.tab1_content, 'style'),
                Output(self.tab2_content, 'style'),
                Output(self.tab3_content, 'style'),
            ],
            Input(self.tabs, 'active_tab')
        )
        def switch_tabs(tab_id):
            tab_ids = ['tab1', 'tab2', 'tab3']
            tab_index = tab_ids.index(tab_id)
            out = [{'display':'none'} for _ in tab_ids]
            out[tab_index] = {'display':'block'}
            return out



