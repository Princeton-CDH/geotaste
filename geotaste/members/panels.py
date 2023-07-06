from ..imports import *
from .components import *

class MemberPanel(FilterPlotPanel, FilterCard):
    desc = 'Member filters'
    records_name='members'

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

    @cached_property
    def subcomponents(self):
        return [
            self.name_card,
            self.membership_year_card,
            self.dob_card,
            self.gender_card,
            self.nation_card,
            self.arrond_card,
        ]
    

    # def component_callbacks(self, app):
    #     super().component_callbacks(app)

        
    #     @app.callback(
    #         [
    #             Output(self.membership_year_card.graph, 'figure'),
    #             Output(self.dob_card.graph, 'figure'),
    #             Output(self.gender_card.graph, 'figure'),
    #             Output(self.nation_card.graph, 'figure'),
    #             Output(self.arrond_card.graph, 'figure'),
    #         ],
    #         Input(self.store, 'data'),
    #         State(self.arrond_card.graph, 'figure'),
    #         prevent_initial_call=True
    #     )
    #     def datastore_updated(panel_data, map_figdata):
    #         filtered_keys = set(panel_data.get('intension',{}).keys())
    #         cards = [
    #             self.membership_year_card, 
    #             self.dob_card, 
    #             self.gender_card, 
    #             self.nation_card, 
    #             self.arrond_card
    #         ]
    #         out = [
    #             (
    #                 dash.no_update 
    #                 if card.key in filtered_keys 
    #                 else card.plot(
    #                     filter_data = panel_data, 
    #                     existing_fig=map_figdata if card is self.arrond_card else None
    #                 )
    #             )
    #             for card in cards
    #         ]
    #         return out