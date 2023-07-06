from ..imports import *
from .components import *


class GeotasteLayout(BaseComponent):
    def __init__(self):
        super().__init__(title="Shakespeare & Co. Labs")
        
    @cached_property
    def panels(self): 
        from ..comparison import PanelComparison
        return PanelComparison()

    @cached_property
    def logo(self):
        return html.Div([
            html.Img(src=LOGO_SRC, className='logo-img'),
            html.H1(self.title, className='logo-title'),
            html.Img(src=LOGO_SRC, className='logo-img'),
        ], className='logo')

    @cached_property
    def navbar(self):
        return dbc.Row([
            dbc.Col(self.logo, className='logo-col', width=4),
            # dbc.Col(self.panels.toptabs, className='toptabs-col', width=8)
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



