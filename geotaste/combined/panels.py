from ..imports import *

class CombinedPanel(FilterCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.member_panel = MemberPanel(**kwargs)
        self.book_panel = BookPanel(**kwargs)
    
    @cached_property
    def content(self):
        return dbc.Container(
            [
                self.member_panel_row, 
                self.book_panel_row
            ], 
            className='combined-panel'
        )
    
    @cached_property
    def member_panel_row(self,params=None): 
        return dbc.Row(
            self.member_panel.layout(params),
            className='member-panel-row'
        )
    @cached_property
    def book_panel_row(self,params=None):
        return dbc.Row(
            self.book_panel.layout(params),
            className='book-panel-row'
        )

    @cached_property
    def map_graph(self):
        return dcc.Graph(figure=self.map_fig.plot(**self._kwargs))

    def component_callbacks(self, app):
        super().component_callbacks(app)

        # @app.callback(
        #     Output(self.store, 'data',allow_duplicate=True),
        #     [ 
        #         Input(self.member_panel.store, 'data'),
        #         Input(self.book_panel.store, 'data'),
        #     ],
        #     prevent_initial_call=True
        # )
        # def component_filters_updated(*filters_d):
        #     self.filter_data = intersect_filters(*filters_d)
        #     return self.filter_data
