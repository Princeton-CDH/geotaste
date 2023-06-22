from ..imports import *
from ..app.components import *
from .datasets import *
from .figs import *


class MemberInputCard(FilterInputCard):
    dataset_class = MembersDataset


class MemberNameCard(MemberInputCard):
    desc = 'Filter by member name'
    key='sort_name'

    @cached_property
    def input(self):
        s=Members().data[self.key]
        return dcc.Dropdown(
            options = [dict(value=lbl, label=lbl) for idx,lbl in zip(s.index, s)],
            value = [],
            multi=True,
            placeholder='Select individual members'
        )



class MemberDOBCard(FilterPlotCard):
    desc = 'Filter by date of birth'
    key='birth_year'
    figure_class = MemberDOBFigure    
    
    
class MembershipYearCard(FilterPlotCard):
    desc = 'Filter by years of membership'
    key='membership_years'
    figure_class = MembershipYearFigure    

class MemberGenderCard(FilterPlotCard):
    desc = 'Filter by gender of member'
    key='gender'
    figure_class = MemberGenderFigure

class MemberNationalityCard(FilterPlotCard):
    desc = 'Filter by nationality of member'
    key='nationalities'
    figure_class = MemberNationalityFigure



class MemberTableCard(FilterTableCard):
    desc = 'Filter by gender of member'
    figure_class = MemberTableFigure

    

class MemberMapCard(FilterPlotCard):
    desc = 'Member addresses mapped'
    # key='gender'
    figure_class = MemberMap


class MemberMapComparisonCard(MemberMapCard): 
    desc = 'Member addresses mapped'
    # key='gender'
    figure_class = ComparisonMemberMap

    @cached_property
    def graph(self):
        # fig=go.Figure()
        # fig.update_layout(height=200)
        return dcc.Graph(figure=MemberMap().plot())
    
    @cached_property
    def table(self):
        return html.Div()
    
    @cached_property
    def body(self):
        return dbc.CardBody([
            self.graph
        ])
    
    @cached_property
    def body_tabs(self):
        return dbc.Tabs([
            dbc.Tab(self.graph, label='Map'),
            dbc.Tab(self.table, label='Table'),
        ])
    

class MemberTableComparisonCard(MemberMapCard): 
    desc = 'Member addresses mapped'
    # key='gender'
    figure_class = ComparisonMemberTable

    @cached_property
    def graph(self): return html.Div()




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
    def map_card(self): return MemberMapCard(**self._kwargs)
    @cached_property
    def table_card(self): return MemberTableCard(**self._kwargs)

    @cached_property
    def store_desc(self): return html.Span(NOFILTER, className='store_desc')
    
    def layout(self, params=None): 
        body = dbc.Container([
            # dbc.Row([
            #     self.store, 
            #     self.store_desc,
            #     self.map_card.layout(params)
            # ]),
            dbc.Row([
                self.store, 
                self.store_desc,
                self.name_card.layout(params),
                self.membership_year_card.layout(params),
                self.dob_card.layout(params),
                self.gender_card.layout(params),
                self.nation_card.layout(params),
                self.map_card.layout(params),
                self.table_card.layout(params)
            ])
        ])
        return body
    

    def component_callbacks(self, app):
        super().component_callbacks(app)

        @app.callback(
            Output(self.store, 'data'),
            [
                Input(self.membership_year_card.store, 'data'),
                Input(self.dob_card.store, 'data'),
                Input(self.gender_card.store, 'data'),
                Input(self.nation_card.store, 'data'),
                Input(self.map_card.store, 'data'),
                # Input(self.table_card.store, 'data'),
            ]
        )
        def component_filters_updated(*filters_d):
            print('component_filters_updated')
            return intersect_filters(*filters_d)
        
        @app.callback(
            [
                Output(self.membership_year_card.graph, 'figure'),
                Output(self.dob_card.graph, 'figure'),
                Output(self.gender_card.graph, 'figure'),
                Output(self.nation_card.graph, 'figure'),
                Output(self.table_card.table, 'children'),
                Output(self.map_card.graph, 'figure'),
            ],
            Input(self.store, 'data'),
            State(self.map_card.graph, 'figure'),
        )
        def datastore_updated(panel_data, map_figdata):
            print('datastore_updated')
            filtered_keys = set(panel_data.get('intension',{}).keys())
            print('filtered_keys',filtered_keys)
            
            cards = [self.membership_year_card, self.dob_card, self.gender_card, self.nation_card, self.table_card, self.map_card]
            out = [
                (
                    dash.no_update 
                    if card.key in filtered_keys 
                    else card.plot(
                        filter_data = panel_data, 
                        existing_fig=map_figdata if card is self.map_card else None
                    )
                )
                for card in cards
            ]
            return out