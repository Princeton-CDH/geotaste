from .imports import *


class GeotasteLayout(BaseComponent):
    def __init__(self):
        super().__init__(title="Shakespeare & Co. Labs")
        
    @cached_property
    def comparison_panel(self): 
        return ComparisonPanel()

    @cached_property
    def logo_popup(self):
        return html.Span([
            dbc.Button(
                self.title,
                id='logo_popup',
                color='link',
                className='logo-title'
            ),
            dbc.Popover(
                [
                    dbc.PopoverHeader('ℹ️ How to use'),
                    dbc.PopoverBody('Filter the left and right hand groups and then compare how their distribute on the map.'),
                ],
                target='logo_popup',
                trigger='hover',
                style={'z-index':1000},
                placement='auto'
            )
        ], className='logo-title')

    @cached_property
    def logo(self):
        return html.Div([
            html.Img(src=LOGO_SRC, className='logo-img'),
            # html.H1(self.title, className='logo-title'),
            self.logo_popup,
            html.Img(src=LOGO_SRC2, className='logo-img2'),
        ], className='logo')
    
    @cached_property
    def frozen_top_row(self):
        return dbc.Container([
            dbc.Row(dbc.Container([
                dbc.Row([self.logo], className='navbar-row'),
                dbc.Row([
                    dbc.Col(self.comparison_panel.content_left_tabs, width=6),
                    dbc.Col(self.comparison_panel.content_right_tabs, width=6),
                ]),
            ]))
        ], className='frozen-top-row')

    def layout(self, params=None):
        return dbc.Container(
            [
                self.frozen_top_row,
                self.comparison_panel.content,
            ],
            className='layout-container'
        )
