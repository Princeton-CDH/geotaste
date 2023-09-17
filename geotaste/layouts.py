from .imports import *


class GeotasteLayout(BaseComponent):
    def __init__(self):
        super().__init__(title="Shakespeare and Company Project Lab")
        
    @cached_property
    def comparison_panel(self): 
        return ComparisonPanel()

    @cached_property
    def logo_popup(self):
        return 

    @cached_property
    def logo(self):
        return 
        

    def layout(self, params=None):
        return dbc.Container([
            ## logo row
            dbc.Row([

                dbc.Col(
                    html.Div([
                        html.Img(src=LOGO_SRC, className='logo-img'),
                        html.Span([
                        dbc.Button(
                                self.title,
                                id='logo_popup',
                                color='link',
                                className='logo-title'
                            ),
                        ], className='logo-title'),

                    ], className='logo'),

                    width=6
                ),


                # dbc.Col(
                #     

                #     width=3
                # ),

                dbc.Col(
                    self.comparison_panel.mainview_tabs,

                    width=6,
                    style={'display':'flex'}
                ),
            ], className='navbar-row'),

            dbc.Row([
                ## actual content layout!
                self.comparison_panel.layout(),

                # welcome modal
                get_welcome_modal(),

                # and progress bar
                # loading spinner
            ], className='content-row'),

            


            dcc.Loading(
                id='layout-loading', 
                children=html.Div(id="layout-loading-output"),
                type='graph', 
                fullscreen=False, 
                style={'background-color':'rgba(255,255,255,0)'},
            ),

            

        ], className='layout-container')
