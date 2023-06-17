from .imports import *




class GeotasteLayout(BaseComponent):
    def __init__(self):
        super().__init__()
        self.navbar = Navbar()
        self.member_panel_comparison = MemberPanelComparison()


    def layout(self, params=None):
        return dbc.Container([
            self.navbar.layout(params),
            dbc.Container(
                self.member_panel_comparison.layout(params),
                className='content-container'
            )
        ], className='layout-container')




class MemberPanelComparison(BaseComponent):
    def __init__(self):
        super().__init__()
        self.navbar = Navbar()
        self.member_panel_L = MemberPanel(name='member_panel_L', color=LEFT_COLOR)
        self.member_panel_R = MemberPanel(name='member_panel_R', color=RIGHT_COLOR)

    def layout(self, params=None):
        return dbc.Container([
            dbc.Row([
                dbc.Col(
                    self.member_panel_L.layout(params),
                    width=6
                ),
                dbc.Col(
                    self.member_panel_R.layout(params),
                    width=6
                ),
            ]),
            
            dbc.Row(
                dbc.Col(
                    self.comparison_map_card.layout(params),
                    width=12,
                    className='comparison_map_card_col'
                )
            )
        ])
    
    @cached_property
    def comparison_map_card(self):
        return MemberMapComparisonCard()
    
    # def component_callbacks(self, app):
    #     @app.callback(
    #         Output(self.comparison_map_card.graph, 'figure'),
    #         [
    #             Input(self.member_panel_L.store, 'data'), 
    #             Input(self.member_panel_R.store, 'data')
    #         ],
    #         State(self.comparison_map_card.graph, 'figure'),
    #     )
    #     def redraw_map(filter_data_L, filter_data_R, old_figdata):
    #         fig_new = MemberComparisonFigureFactory(filter_data_L, filter_data_R).plot_map()
    #         fig_old = go.Figure(old_figdata)
    #         fig_out = go.Figure(
    #             layout=fig_old.layout if fig_old.data else fig_new.layout,
    #             data=fig_new.data
    #         )
    #         return fig_out
        


            



   
  






class Navbar(BaseComponent):
    def layout(self, params=None):
        return get_navbar()
