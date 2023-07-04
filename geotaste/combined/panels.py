from ..imports import *

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
