from .imports import *


class GeotasteLayout(BaseComponent):
    def __init__(self):
        super().__init__(title="Shakespeare & Co. Labs")
        
    @cached_property
    def comparison_panel(self): 
        return ComparisonPanel()

    @cached_property
    def logo(self):
        return html.Div([
            html.Img(src=LOGO_SRC, className='logo-img'),
            html.H1(self.title, className='logo-title'),
            html.Img(src=LOGO_SRC, className='logo-img'),
        ], className='logo')

    def layout(self, params=None):
        return dbc.Container(
            [
                dbc.Row([self.logo], className='navbar-row'),
                self.comparison_panel.layout()
            ],
            className='layout-container'
        )

