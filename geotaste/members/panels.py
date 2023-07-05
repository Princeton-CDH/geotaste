from ..imports import *
from .components import *

class MemberPanel(FilterCard):
    @cached_property
    def name_card(self): return MemberNameCard(**self._kwargs)
    @cached_property
    def dob_card(self): return MemberDOBCard(**self._kwargs)
    @cached_property
    def membership_year_card(self): return MembershipYearCard(**self._kwargs)
    @cached_property
    def gender_card(self): return MemberGenderCard(**self._kwargs)
    @cached_property
    def nation_card(self): return MemberNationalityCard(**self._kwargs)
    @cached_property
    def arrond_card(self): return MemberArrondCard(**self._kwargs)
    
    def layout(self, params=None): 
        body = dbc.Container([
            dbc.Row([
                self.store, 
                self.name_card.layout(params),
                self.membership_year_card.layout(params),
                self.dob_card.layout(params),
                self.gender_card.layout(params),
                self.nation_card.layout(params),
                self.arrond_card.layout(params),
                self.store_desc,
            ])
        ])
        return body
    

    def component_callbacks(self, app):
        super().component_callbacks(app)

        @app.callback(
            Output(self.store, 'data'),
            [
                Input(self.name_card.store, 'data'),
                Input(self.membership_year_card.store, 'data'),
                Input(self.dob_card.store, 'data'),
                Input(self.gender_card.store, 'data'),
                Input(self.nation_card.store, 'data'),
                Input(self.arrond_card.store, 'data'),
            ]
        )
        def component_filters_updated(*filters_d):
            self.filter_data = intersect_filters(*filters_d)
            return self.filter_data
        
        @app.callback(
            [
                Output(self.membership_year_card.graph, 'figure'),
                Output(self.dob_card.graph, 'figure'),
                Output(self.gender_card.graph, 'figure'),
                Output(self.nation_card.graph, 'figure'),
                Output(self.arrond_card.graph, 'figure'),
            ],
            Input(self.store, 'data'),
            State(self.arrond_card.graph, 'figure'),
        )
        def datastore_updated(panel_data, map_figdata):
            filtered_keys = set(panel_data.get('intension',{}).keys())
            cards = [
                self.membership_year_card, 
                self.dob_card, 
                self.gender_card, 
                self.nation_card, 
                self.arrond_card
            ]
            out = [
                (
                    dash.no_update 
                    if card.key in filtered_keys 
                    else card.plot(
                        filter_data = panel_data, 
                        existing_fig=map_figdata if card is self.arrond_card else None
                    )
                )
                for card in cards
            ]
            return out