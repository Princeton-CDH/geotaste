from ..imports import *
from .components import *

class BookPanel(FilterCard):
    @cached_property
    def year_card(self): return BookYearCard(**self._kwargs)
    
    def layout(self, params=None):
        body = dbc.Container([
            html.Div(self.store_desc, style={'textAlign':'center'}),
            self.year_card.layout(params),
            self.store
        ])
        return body
    
    def component_callbacks(self, app):
        super().component_callbacks(app)

        @app.callback(
            Output(self.store, 'data'),
            [
                Input(self.year_card.store, 'data'),
            ]
        )
        def component_filters_updated(*filters_d):
            print('component_filters_updated')
            self.filter_data = intersect_filters(*filters_d)
            return self.filter_data
        