from .imports import *

class GeotasteLayout(BaseComponent):
    """
    The GeotasteLayout class inherits from the BaseComponent class and 
    is used to define the layout and properties for the Geotaste Project.
    """

    def __init__(self):
        """
        Initializes the GeotasteLayout class with a title.
        """
        super().__init__(title=SITE_TITLE)
        
    @cached_property
    def comparison_panel(self):
        """
        Defines a cached property that returns an instance of the ComparisonPanel.
        """
        return ComparisonPanel()
        

    def layout(self, params=None):
        """
        Defines the layout for the GeotasteLayout. This includes the logo row,
        navigation bar, actual content layout, and a loading spinner.
        """
        return dbc.Container([
            # logo row
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
                dbc.Col(
                    self.comparison_panel.mainview_tabs,
                    width=6,
                    style={'display':'flex'}
                ),
            ], className='navbar-row'),

            dbc.Row([
                # actual content layout
                self.comparison_panel.layout(),
                # welcome modal
                get_welcome_modal(),
            ], className='content-row'),

            dcc.Loading(
                id='layout-loading', 
                children=html.Div(id="layout-loading-output"),
                type='graph', 
                fullscreen=False, 
                style={'background-color':'rgba(255,255,255,0)'},
            ),

            dcc.Location(id='url-output', refresh="callback-nav"),
            dcc.Location(id='url-input', refresh="callback-nav"),

            dbc.Button(
                'ⓘ',
                color="link",
                n_clicks=0,
                id='welcome_modal_info_btn',
            ),

            dbc.Container(DONOTCITE, id='donotcite')

        ], className='layout-container')



    def component_callbacks(self, app):
        """
        """
        super().component_callbacks(app)

        ### SWITCHING TABS

        @app.callback(
            Output('welcome-modal','is_open',allow_duplicate=True),
            Input('welcome_modal_info_btn', 'n_clicks'),
            State('welcome-modal', 'is_open'),
            prevent_initial_call=True
        )
        def toggle_welcome_modal(n_clicks, is_open):
            return not is_open