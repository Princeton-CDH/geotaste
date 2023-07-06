from ..imports import *
from .components import *

class BookPanel(FilterCard):
    @cached_property
    def content(self,params=None):
        body = dbc.Container([
            html.Div(self.store_desc, style={'textAlign':'center'}),
            self.year_card.layout(params),
            self.store
        ])
        return body

    @cached_property
    def year_card(self): return BookYearCard(**self._kwargs)
    





    # def component_callbacks(self, app):
    #     super().component_callbacks(app)

        # @app.callback(
        #     Output(self.store, 'data', allow_duplicate=True),
        #     [
        #         Input(self.year_card.store, 'data'),
        #     ],
        #     prevent_initial_call=True
        # )
        # def component_filters_updated(*filters_d):
        #     print('component_filters_updated')
        #     self.filter_data = intersect_filters(*filters_d)
        #     return self.filter_data
        