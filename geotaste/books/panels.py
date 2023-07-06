from ..imports import *
from .components import *

class BookPanel(FilterPanel, FilterCard):
    desc = 'Book filters'
    records_name='books'

    
    @cached_property
    def year_card(self): return BookYearCard(**self._kwargs)
    
    @cached_property
    def subcomponents(self):
        return [self.year_card]





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
        