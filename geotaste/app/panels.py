from ..imports import *
from .components import FilterComponent

class FilterPanel(FilterComponent):
    @cached_property
    def subcomponents(self):
        return []  # subclass this
    @cached_property
    def graph_subcomponents(self):
        return [
            card for card in self.subcomponents
            if hasattr(card,'graph')
        ]
    

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
        



class FilterPlotPanel(FilterPanel):
    def component_callbacks(self, app):
        super().component_callbacks(app)
        @app.callback(
            [
                Output(card.graph,'figure',allow_duplicate=True)
                for card in self.graph_subcomponents
            ],
            Input(self.store, 'data'),
            prevent_initial_call=True
        )
        def redraw_graphs_from_new_data(panel_data):
            filtered_keys = set(panel_data.get('intension',{}).keys())
            return [
                (
                    dash.no_update 
                    if card.key in filtered_keys 
                    else card.plot(
                        filter_data = panel_data, 
                    )
                )
                for card in self.graph_subcomponents
            ]