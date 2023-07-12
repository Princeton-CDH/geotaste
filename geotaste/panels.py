from .imports import *
from .views import *


class FilterPanel(FilterComponent):
    @cached_property
    def content(self,params=None):
        return dbc.Container([self.store, self.store_str] + super().content.children)
    
    @cached_property
    def store_str(self):
        return dcc.Store(id=self.id(self.name)+'_str', data='')


    @cached_property
    def store_desc(self): 
        return dbc.Textarea(
            id=self.id('query_str'), 
            className='store_desc query_str', 
            placeholder=UNFILTERED, 
            value='', 
            style={'color':self.color}
        )
    
    @cached_property
    def button_query(self):
        return dbc.Button(
            "Query", 
            color="link", 
            n_clicks=0,
            className='button_query',
            id=self.id('button_query')
        )

    def component_callbacks(self, app):
        super().component_callbacks(app)
        
        # intersect and listen
        if self.store_subcomponents:
            @app.callback(
                [
                    Output(self.store, 'data', allow_duplicate=True),
                    Output(self.store_desc, 'value', allow_duplicate=True),
                ],
                [
                    Input(card.store, 'data')
                    for card in self.store_subcomponents
                ],
                prevent_initial_call=True
            )
            def subcomponent_filters_updated(*filters_d):
                logger.debug('subcomponent filters updated')
                self.filter_data = self.intersect_filters(*filters_d)
                self.filter_query = Combined().filter_query_str(self.filter_data)
                return self.filter_data, self.filter_query
            
            @app.callback(
                Output(self.store_str, 'data'),
                Input(self.button_query, 'n_clicks'),
                State(self.store_desc, 'value'),
                prevent_initial_call=True
            )
            def update_filter_query(n_clicks, query_str):
                logger.debug(f'setting {query_str} to {self.name}.store_str')
                return query_str
            
        


class FilterPlotPanel(FilterPanel):
    def component_callbacks(self, app):
        super().component_callbacks(app)

        if self.graph_subcomponents:
            @app.callback(
                [
                    Output(card.graph,'figure',allow_duplicate=True)
                    for card in self.graph_subcomponents
                ],
                [
                    Input(self.store, 'data'),
                    Input(self.store_str, 'data')
                ],
                prevent_initial_call=True
            )
            def redraw_graphs_from_new_data(filter_data, query_str):
                logger.debug(f'redrawing, triggered by {ctx.triggered_id}')
                fd = query_str if ctx.triggered_id == self.store_str.id else filter_data
                logger.debug(fd)
                filtered_keys = set(filter_data.keys())

                # filter_data, existing_fig, kwargs
                existing_fig = None # @TODO?
                
                return [
                    (
                        dash.no_update 
                        if card.key in filtered_keys 
                        else card.plot(fd, existing_fig=existing_fig)
                    )
                    for card in self.graph_subcomponents
                ]
            
class CollapsiblePanel(CollapsibleCard):
    body_is_open = True

class MemberPanel(CollapsiblePanel):
    name='MP'
    figure_factory = CombinedFigureFactory
    desc = 'Member Filters'
    records_name='members'

    @cached_property
    def name_card(self): 
        return MemberNameCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def dob_card(self): 
        return MemberDOBCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def membership_year_card(self): 
        return MembershipYearCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def gender_card(self): 
        return MemberGenderCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def nation_card(self): 
        return MemberNationalityCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def arrond_card(self): 
        return MemberArrondCard(name_context=self.name, **self._kwargs)

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

    @cached_property
    def store_subcomponents(self): return []
    @cached_property
    def graph_subcomponents(self): return []
    
    

class BookPanel(CollapsiblePanel):
    name='BP'
    figure_factory = CombinedFigureFactory
    desc = 'Book Filters'
    records_name='books'

    @cached_property
    def title_card(self): 
        return BookTitleCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def year_card(self): 
        return BookYearCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def genre_card(self): 
        return BookGenreCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def creator_card(self):
        return CreatorNameCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def creator_gender_card(self):
        return CreatorGenderCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def creator_nationality_card(self):
        return CreatorNationalityCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def subcomponents(self):
        return [
            self.title_card,
            self.year_card,
            self.genre_card,
            self.creator_card,
            self.creator_gender_card,
            self.creator_nationality_card,
        ]

    @cached_property
    def store_subcomponents(self): return []
    @cached_property
    def graph_subcomponents(self): return []
    
    



class EventPanel(CollapsiblePanel):
    name='EP'
    figure_factory = CombinedFigureFactory
    desc = 'Event Filters'
    records_name='events'

    @cached_property
    def year_card(self): 
        return EventYearCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def type_card(self): 
        return EventTypeCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def subcomponents(self):
        return [
            self.year_card,
            self.type_card,
        ]

    @cached_property
    def store_subcomponents(self): return []
    @cached_property
    def graph_subcomponents(self): return []


class CombinedPanel(FilterPlotPanel):
    
    @cached_property
    def member_panel(self): 
        return MemberPanel(name_context=self.name, **self._kwargs)

    @cached_property
    def book_panel(self):
        return BookPanel(name_context=self.name, **self._kwargs)
    
    @cached_property
    def event_panel(self):
        return EventPanel(name_context=self.name, **self._kwargs)

    @cached_property
    def subcomponents(self):
        return [
            self.member_panel,
            self.book_panel,
            self.event_panel,
        ]
    
    @cached_property
    def store_subcomponents(self):
        return [
            card
            for panel in self.subcomponents
            for card in panel.subcomponents
            if hasattr(card,'store')
        ]
    
    @cached_property
    def graph_subcomponents(self):
        return [
            card
            for panel in self.subcomponents
            for card in panel.subcomponents
            if hasattr(card,'graph')
        ]
    



class ComparisonPanel(BaseComponent):
    figure_factory = ComparisonFigureFactory
    # default_view = MemberMapView

    @cached_property
    def content_left_tabs(self,params=None):
        return dbc.Container(dbc.Row([
            dbc.Col(
                # html.P(['Left Group: ',self.L.store_desc]), 
                [self.L.store_desc, self.L.button_query],
                width=6, 
                className='storedescs-col storedescs-col-L left-color'
            ),
            
            dbc.Col(
                [self.R.store_desc, self.R.button_query],
                width=6, 
                className='storedescs-col storedescs-col-R right-color'
            ),
        ]), className='layout-toprow')
    
    
    @cached_property
    def content_right_tabs(self,params=None):
        return dbc.Container([
            dbc.Row(self.graphtabs, className='content-tabs-row')
        ])

    @cached_property
    def content_right(self,params=None):
        return dbc.Container([
            dbc.Row(self.graphtab, className='content-belowtabs-row')
        ], className='layout-rightcol')
    
    @cached_property
    def content_main_row(self,params=None):
        return dbc.Row([
            dbc.Col(
                self.L.layout(params), 
                width=6, 
                className='panel_L panel'
            ),
            
            dbc.Col(
                self.R.layout(params), 
                width=6, 
                className='panel_R panel'
            ),
        ], 
        className='layout-mainrow')
    
    @cached_property
    def content_left(self,params=None):
        return dbc.Container(self.content_main_row, className='layout-leftcol')

    @cached_property
    def content(self,params=None):
        return dbc.Container([
            self.content_left_tabs,

            dbc.Row([
                dbc.Col(self.content_left, className='layout-leftcol', width=6),
                dbc.Col(self.content_right, className='layout-rightcol', width=6)
            ])
        ], className='panel-comparison-layout layout-belownavbar')
        
    @cached_property
    def subcomponents(self): return (self.L, self.R)

    @cached_property
    def L(self): 
        return CombinedPanel(
            name='L',
            L_or_R='L', 
            color=LEFT_COLOR,
            desc='Left-hand Group Panel'
        )
    
    @cached_property
    def R(self): 
        return CombinedPanel(
            name='R',
            L_or_R='R',
            color=RIGHT_COLOR,
            desc='Right-hand Group Panel'
        )
    
    @cached_property
    def graphtabs(self):
        map_tabs = get_tabs([
            dict(label='Left vs. Right Groups', tab_id='map_LR'),
            # dict(label='Left Group', tab_id='map_L'),
            # dict(label='Right', tab_id='map_R'),
        ], tab_level=2, className='graphtabs-container')
        
        tbl_tabs = get_tabs(
            children=[
                dict(label='By member', tab_id='tbl_members'),                
                dict(label='By arrondissement', tab_id='tbl_arrond'),
            ], 
            tab_level=2, className='graphtabs-container', active_tab='tbl_members'
        )

        analyze_tabs = get_tabs(
            children=[
                dict(
                    label='Magnitude of difference',
                    tab_id='tbl_diff'),                
            ], 
            tab_level=2, 
            className='graphtabs-container'
        )

        graphtabs = get_tabs(
            children=[
                dict(children=map_tabs, label='Map data', tab_id='map'),
                dict(children=tbl_tabs, label='View data', tab_id='tbl'),
                # dict(children=analyze_tabs, label='Analyze data', tab_id='analyze')
            ], 
            tab_level=1, 
            className='graphtabs-container',
            active_tab='map'
        )
        return dbc.Container(graphtabs, className='graphtabs-container-container')
    
    @cached_property
    def graphtab(self):
        return dbc.Container(
            children=[html.Pre('Loading...')],
            className='graphtab-div',
            id=self.id('graphtab')
        )

    def component_callbacks(self, app):
        # super().component_callbacks(app)


        @app.callback(
            Output(self.graphtab, 'children'),
            [
                Input({"type": "tab_level_1", "index": ALL}, "active_tab"),
                Input({"type": "tab_level_2", "index": ALL}, "active_tab"),
                Input(self.L.store, 'data'),
                Input(self.L.store_str, 'data'),
                Input(self.R.store, 'data'),
                Input(self.R.store_str, 'data'),
            ],
        )
        def repopulate_graphtab(tab_ids_1, tab_ids_2, filter_data_L, filter_query_L, filter_data_R, filter_query_R):
            fdL = filter_query_L if ctx.triggered_id == self.L.store_str.id else filter_data_L
            fdR = filter_query_R if ctx.triggered_id == self.R.store_str.id else filter_data_R
            serialized_data = serialize([tab_ids_1, tab_ids_2, fdL, fdR])
            return graphtab_cache(serialized_data)
            

@cache
def graphtab_cache(serialized_data):
    logger.debug(f'graphtab_cache({serialized_data})')
    tab_ids_1, tab_ids_2, fdL, fdR = unserialize(serialized_data)
    ff = ComparisonFigureFactory(fdL, fdR)
    viewfunc = determine_view(tab_ids_1, tab_ids_2)
    return viewfunc(ff)


def determine_view(tab_ids_1=[], tab_ids_2=[], default=MemberMapView):
    tab_ids_1_set=set(tab_ids_1)
    tab_ids_2_set=set(tab_ids_2)

    if 'tbl' in tab_ids_1_set:
        if 'tbl_members' in tab_ids_2_set: 
            return MemberTableView
            
        elif 'tbl_arrond' in tab_ids_2_set:
            return ArrondTableView
            
    elif 'analyze' in tab_ids_1_set:
        if 'tbl_diff' in tab_ids_2_set:
            return DifferenceDegreeView
    
    elif 'map' in tab_ids_1_set:
        return MemberMapView
        if 'map_L' in tab_ids_2_set: return 'map_members_L'
        if 'map_R' in tab_ids_2_set: return 'map_members_R'
        return 'map_members'
    
    return default