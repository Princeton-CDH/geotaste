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
            html.Img(src=LOGO_SRC2, className='logo-img2'),
        ], className='logo')

    def layout(self, params=None):
        return dbc.Container(
            [
                dbc.Container([
                    dbc.Row(dbc.Container([
                        dbc.Row([self.logo], className='navbar-row'),
                        dbc.Row([
                            dbc.Col(self.comparison_panel.content_left_tabs, width=6),
                            dbc.Col(self.comparison_panel.content_right_tabs, width=6),
                        ]),
                    ]))
                ], className='frozen-top-row'),
                
                self.comparison_panel.content_left,
                self.comparison_panel.content_right,
            ],
            className='layout-container'
        )

