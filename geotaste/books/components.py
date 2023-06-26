from ..imports import *
from .figs import *
from ..app.components import FilterPlotCard, FilterCard

class BookYearCard(FilterPlotCard):
    desc = 'Date of book\'s publication'
    key='year'
    figure_class = BookYearFigure

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
        
        # @app.callback(
        #     [
        #         Output(self.membership_year_card.graph, 'figure'),
        #         Output(self.dob_card.graph, 'figure'),
        #         Output(self.gender_card.graph, 'figure'),
        #         Output(self.nation_card.graph, 'figure'),
        #         Output(self.table_card.table, 'children'),
        #         Output(self.map_card.graph, 'figure'),
        #     ],
        #     Input(self.store, 'data'),
        #     State(self.map_card.graph, 'figure'),
        # )
        # def datastore_updated(panel_data, map_figdata):
        #     print('datastore_updated')
        #     filtered_keys = set(panel_data.get('intension',{}).keys())
            
        #     cards = [self.membership_year_card, self.dob_card, self.gender_card, self.nation_card, self.table_card, self.map_card]
        #     out = [
        #         (dash.no_update if card.key in filtered_keys else card.plot(panel_data))
        #         for card in cards
        #     ]
        #     if out[-1]!=dash.no_update:
        #         new_fig = out[-1]
        #         old_fig = go.Figure(map_figdata)
        #         out_fig = go.Figure(data=new_fig.data, layout=old_fig.layout)
        #         out[-1] = out_fig
        #     return out

            