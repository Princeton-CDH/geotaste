from ..imports import *
from .components import FilterComponent

class FilterPanel(FilterComponent):
    @cached_property
    def subcomponents(self):
        return []  # subclass this
    
    @cached_property
    def content(self,params=None):
        cards=[
            card.layout(params)
            for card in self.subcomponents
        ]
        return dbc.Container([self.store] + cards)
    
    def component_callbacks(self, app):
        super().component_callbacks(app)
        
        # intersect and listen
        @app.callback(
            Output(self.store, 'data',allow_duplicate=True),
            [
                Input(card.store, 'data')
                for card in self.subcomponents
            ],
            prevent_initial_call=True
        )
        def subcomponent_filters_updated(*filters_d):
            self.log('subcomponent filters updated')
            self.filter_data = self.intersect_filters(*filters_d)
            return self.filter_data