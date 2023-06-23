from ..imports import *
from .components import *
from ..members.components import *
from ..books.components import *

STYLE_INVIS={'display':'none'}
STYLE_VIS={'display':'block'}

STYLE_INVIS={'opacity':0}
STYLE_VIS={'opacity':1}

STYLE_INVIS={'visibility':'hidden'}
STYLE_VIS={'visibility':'visible'}

STYLE_INVIS = {'position': 'absolute', 'top': '-9999px', 'left': '-9999px'}
STYLE_VIS = {'position': 'relative'}

class GeotasteLayout(BaseComponent):
    def __init__(self):
        super().__init__(title="Geography of Taste")
        self.panels = PanelComparison()
        self.ticker = dcc.Interval(interval=1*1000, n_intervals=0)
        self.last_window_size = None


    @cached_property
    def logo(self):
        return html.Div([
            html.Img(src=LOGO_SRC, className='logo-img'),
            html.H1(self.title, className='logo-title'),
        ], className='logo')

    @cached_property
    def navbar(self):
        return dbc.Row(self.logo, className='navbar-row')
    
    @cached_property
    def content(self):
        return dbc.Row(self.panel_comparison.layout())

    @cached_property
    def store_window_size(self): 
        return html.Div(style={'display':'none'})
    
    @cached_property
    def top_row(self, params=None):
        return dbc.Row(self.layout_top(params), className='layout-toprow')
    @cached_property
    def main_row(self, params=None):
        return dbc.Row(self.layout_main(params), className='layout-mainrow')

    def layout(self, params=None):
        return dbc.Container([
                self.store_window_size,
                self.top_row,
                self.main_row,
                self.ticker,
        ], className='layout-container')

    def layout_top(self, params=None):
        return dbc.Container([
            dbc.Row(self.logo, className='navbar-row'),
            dbc.Row(self.panels.layout_top(params), className='content-row')
        ], className='layout-container')
    
    def layout_main(self, params=None):
        return self.panels.layout_main(params)
    

    def component_callbacks(self, app):
        app.clientside_callback(
                """
                function(obj) {
                    var w = window.innerWidth;
                    var h = window.innerHeight;
                    return JSON.stringify({'height': h, 'width': w});
                }
                """,
                Output(self.store_window_size, 'children'),
                Input(self.ticker, 'n_intervals'),
            )
        

        @app.callback(
            Output(self.main_row, 'style'),
            Input(self.store_window_size, 'children'),
        )
        def screen_size_changed(xstr, n=0, height_top=400, min_height=100):
            x=json.loads(xstr)
            height = x.get('height')
            if height and height > (height_top+min_height):
                return {
                    'height':f'{height - height_top}px', 
                    # 'border':'1px solid red'
                }
            raise PreventUpdate


class PanelComparison(BaseComponent):
    def __init__(self, *x, **y):
        super().__init__(*x,**y)
        self.L = LeftPanel()
        self.R = RightPanel()
        
    def layout_top(self, params=None):
        return html.H2('Top')
    
    def layout_main(self, params=None):
        return dbc.Container([
            self.layout_dueling_panels(params)
        ])
    
    def layout_dueling_panels(self, params=None):
        return dbc.Row([
            dbc.Col(self.L.layout(params), width=6, className='panel_L panel'),
            dbc.Col(self.R.layout(params), width=6, className='panel_R panel'),
        ])
    







class MemberBookEventPanel(FilterComponent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.member_panel = MemberPanel(**kwargs)
        # self.book_panel = BookPanel(**kwargs)

    def layout(self, params=None):
        return dbc.Container([
            self.store,
            dbc.Row(self.member_panel.layout(params)),
            # dbc.Row(self.book_panel.layout(params))
        ])
    

    def component_callbacks(self, app):
        super().component_callbacks(app)

        @app.callback(
            Output(self.store, 'data'),
            [
                Input(self.member_panel.store, 'data'),
            ]
        )
        def component_filters_updated(*filters_d):
            return intersect_filters(*filters_d)


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





    # def dual_map_row(self, params=None):
    #     return dbc.Row([
    #         dbc.Col(self.panel_L.map_card.layout(params, header=False), width=6),
    #         dbc.Col(self.panel_R.map_card.layout(params, header=False), width=6),
    #     ], className='bimap-row')
    

    
    # def dual_store_descs(self, params=None):
    #     return dbc.Row([
    #         dbc.Col(html.H2(['Left Group: ', self.panel_L.store_desc]), width=6, className='storedescs-col storedescs-col-L left-color'),
    #         dbc.Col(html.H2(['Right Group: ', self.panel_R.store_desc]), width=6, className='storedescs-col storedescs-col-R right-color'),
    #     ], className='storedescs-row')
    
    


    # @cached_property
    # def comparison_map_card(self): return MemberMapComparisonCard()
    

    
    # @cached_property
    # def toptabs(self):
    #     return dbc.Tabs([
    #         dbc.Tab(label='Juxtapose', tab_id='0'),
    #         dbc.Tab(label='Contrast', tab_id='1'),
    #     ], className='tabs-container', active_tab='0')

    # @cached_property
    # def toptab1(self, params=None):
    #     return html.Div(self.dual_map_row(params), style=STYLE_INVIS)
    
    # @cached_property
    # def toptab2(self, params=None):
    #     return html.Div(self.comparison_map_card.layout(params), style=STYLE_INVIS)
    
    # @cached_property
    # def toptab(self): return html.Div(BLANKSTR)
    

    
    




    # def component_callbacks(self, app):
    #     @app.callback(
    #         [
    #             Output(self.toptab1, 'style'),
    #             Output(self.toptab2, 'style'),
    #         ],
    #         Input(self.toptabs, 'active_tab')
    #     )
    #     def switch_tabs(tab_id, num_tabs=2):
    #         tab_index = int(tab_id)
    #         assert tab_index < num_tabs
    #         out = [STYLE_INVIS for _ in range(num_tabs)]
    #         out[tab_index] = STYLE_VIS
    #         return out


        # @app.callback(
        #     [
        #         Output(self.comparison_map_card.graph, 'figure'),
        #         Output(self.comparison_map_card.table, 'children'),
        #     ],
        #     [
        #         Input(self.panel_L.store, 'data'), 
        #         Input(self.panel_R.store, 'data')
        #     ],
        #     State(self.comparison_map_card.graph, 'figure'),
        # )
        # def redraw_map(filter_data_L, filter_data_R, old_figdata):
        #     print('redraw_map')
        #     fig = ComparisonMemberMap(
        #         filter_data_L,
        #         filter_data_R
        #     )
        #     fig_new = fig.plot()
        #     fig_old = go.Figure(old_figdata)
        #     ofig = go.Figure(
        #         layout=fig_old.layout if fig_old.data else fig_new.layout,
        #         data=fig_new.data
        #     )

        #     # table
        #     # print(fig.df_arronds)
        #     table_fig = ComparisonMemberTable(
        #         df=round(fig.df_arronds,2).reset_index(),    
        #     )
        #     table_ofig = table_fig.plot()
        #     return [ofig, table_ofig]