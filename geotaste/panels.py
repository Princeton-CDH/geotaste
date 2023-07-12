from .imports import *
from .views import *


class FilterPanel(FilterComponent):
    @cached_property
    def content(self,params=None):
        return dbc.Container([self.store] + super().content.children)
    
    @cached_property
    def store_desc(self): 
        return dbc.Container(
            UNFILTERED,
            id=self.id('query_str'), 
            className='store_desc query_str', 
            # placeholder=UNFILTERED, 
            # value='', 
            style={'color':self.color}
        )


    def component_callbacks(self, app):
        super().component_callbacks(app)
        
        # intersect and listen
        if self.store_subcomponents:
            @app.callback(
                [
                    Output(self.store, 'data', allow_duplicate=True),
                    Output(self.store_desc, 'children', allow_duplicate=True),
                ],
                [
                    Input(card.store, 'data')
                    for card in self.store_subcomponents
                ],
                prevent_initial_call=True
            )
            #@logger.catch
            def subcomponent_filters_updated(*filters_d):
                logger.debug('subcomponent filters updated')
                filter_data = self.intersect_filters(*filters_d)
                filter_desc = Combined().filter_query_str(filter_data)
                return filter_data, filter_desc
            
            @app.callback(
                [
                    Output(card.store_panel, 'data', allow_duplicate=True)
                    for card in self.store_panel_subcomponents
                ],
                Input(self.store, 'data'),
                [
                    State(card.store_panel, 'data')
                    for card in self.store_panel_subcomponents
                ],
                prevent_initial_call=True
            )
            #@logger.catch
            def panel_filter_data_changed(panel_filter_data, *old_filter_data_l):
                if panel_filter_data is None: panel_filter_data={}
                logger.debug(f'panel_filter_data_changed({panel_filter_data})')


                logger.debug([card.key for card in self.store_panel_subcomponents])

                new_filter_data_l = [
                    {k:v for k,v in panel_filter_data.items() if k!=card.key}
                    for card in self.store_panel_subcomponents    
                ]
                out = [
                    (dash.no_update if old==new else new)
                    for old,new in zip(old_filter_data_l, new_filter_data_l)
                ]
                logger.debug(f'out from panel {pformat(out)}')
                return out
            

            

        


class FilterPlotPanel(FilterPanel):
    def component_callbacks(self, app):
        super().component_callbacks(app)

        # if self.graph_subcomponents:
        #     @app.callback(
        #         [
        #             Output(card.graph,'figure',allow_duplicate=True)
        #             for card in self.graph_subcomponents
        #         ],
        #         [
        #             Input(self.store, 'data'),
        #         ],
        #         [
        #             State(card.body,'is_open')
        #             for card in self.graph_subcomponents
        #         ],
        #         prevent_initial_call=True
        #     )
        #     def redraw_graphs_from_new_data(filter_data, *cards_open):
        #         logger.debug(f'redraw_graphs_from_new_data({filter_data})')
        #         filtered_keys = set(filter_data.keys())
        #         existing_fig = None # @TODO?
                
        #         return [
        #             (
        #                 dash.no_update 
        #                 if (
        #                     card.key in filtered_keys 
        #                     or 
        #                     not cards_open[i]
        #                 )
        #                 else card.plot(
        #                     filter_data, 
        #                     existing_fig=existing_fig
        #                 )
        #             )
        #             for i,card in enumerate(self.graph_subcomponents)
        #         ]
            
class CollapsiblePanel(CollapsibleCard):
    body_is_open = True

class MemberPanel(CollapsiblePanel):
    name='MP'
    figure_factory = CombinedFigureFactory
    desc = 'Members of the library'
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
    desc = 'The books they borrowed'
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
    def event_year_card(self): 
        return EventYearCard(name_context=self.name, **self._kwargs)
        
    @cached_property
    def subcomponents(self):
        return [
            self.title_card,
            self.year_card,
            self.genre_card,
            self.creator_card,
            self.creator_gender_card,
            self.creator_nationality_card,
            self.event_year_card,
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
    def subcomponents(self):
        return [
            self.member_panel,
            self.book_panel,
        ]
    
    def cards_with_attr(self, attrname:str):
        return [
            card
            for panel in self.subcomponents
            for card in panel.subcomponents
            if hasattr(card,attrname)
        ]



class ComparisonPanel(BaseComponent):
    figure_factory = ComparisonFigureFactory
    # default_view = MemberMapView

    @cached_property
    def content_left_tabs(self,params=None):
        return dbc.Container(dbc.Row([
            dbc.Col(
                html.P(['Left Group: ',self.L.store_desc]), 
                # [self.L.store_desc],
                width=6, 
                className='storedescs-col storedescs-col-L left-color'
            ),
            
            dbc.Col(
                html.P(['Right Group: ',self.R.store_desc]), 
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
                Input(self.R.store, 'data'),
            ],
        )
        #@logger.catch
        def repopulate_graphtab(*args):
            serialized_data = serialize(args)
            return graphtab_cache(serialized_data)
            

# @cache

@cache_obj.memoize()
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