from .imports import *
from .views import *


class FilterPanel(FilterComponent):
    @cached_property
    def content(self,params=None):
        return dbc.Container([self.store] + super().content.children)
    
    @cached_property
    def store_desc(self): 
        return html.Span(
            UNFILTERED,
            id=self.id('query_str'), 
            className='store_desc query_str', 
            # placeholder=UNFILTERED, 
            # value='', 
            # style={'color':self.color}
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
            #@logger.catch
            )
            def subcomponent_filters_updated(*filters_d):
                logger.debug('subcomponent filters updated')
                filter_data = self.intersect_filters(*filters_d)
                filter_desc = filter_query_str(filter_data, human=True) if filter_data else UNFILTERED
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
    className='collapsible-panel'


class MemberPanel(CollapsiblePanel):
    name='MP'
    figure_factory = CombinedFigureFactory
    desc = 'Members of the library'
    records_name='members'
    tooltip = 'Filter members of the library by name, date of birth, when active, gender, nationality, and arrondissement'

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
    desc = 'Books they borrowed'
    records_name='books'
    tooltip = 'Filter books borrowed by title, date of publication, genre, author, author gender, author nationality, and the date borrowed'

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
    def event_month_card(self): 
        return EventMonthCard(name_context=self.name, **self._kwargs)
        
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
            self.event_month_card,
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
        p_L=html.Span([html.B('Group 1: '), self.L.store_desc])
        p_R=html.Span([html.B('Group 2: '), self.R.store_desc])
        
        def getbtn(x, cls=''):
            className='button_store_desc store_desc query_str'
            idx=dict(type='store_desc_btn', index=uid())
            msg=f'(Click here to show/hide the filters). Here, {cls}-hand side in {"blue" if cls=="right" else "brown"}, filter for a group of library members and/or the books they borrowed. Then, see how it compare with the {"left" if cls=="right" else "right"}-hand group, on the map and in the data.'
            return dbc.Container([
                dbc.Button(
                    x, 
                    color="link", 
                    n_clicks=0,
                    className=className,
                    id=idx,
                    style={'text-align':'center'}
                ),
                # dbc.Popover(
                #     [
                #         dbc.PopoverHeader(f'ℹ️ Choose books/members for {cls}-hand group'),
                #         dbc.PopoverBody(),
                #     ],
                #     target=idx,
                #     trigger='hover',
                #     style={'z-index':1000},
                #     placement='right'
                # )
                dbc.Tooltip(msg, target=idx)
            ])


        
        btn_L = getbtn(p_L, cls='left')
        btn_R = getbtn(p_R, cls='right')

        return dbc.Container(
            dbc.Row([
                dbc.Col(
                    btn_L,
                    className='storedescs-col storedescs-col-L'
                ),
                dbc.Col(
                    html.Nobr(), 
                    className='storedescs-inbetween',
                    width=1
                ),
                dbc.Col(
                    btn_R,
                    className='storedescs-col storedescs-col-R'
                ),
            ]), 
            className='layout-toprow'
        )
    
    
    @cached_property
    def content_right_tabs(self,params=None):
        return dbc.Container([
            dbc.Row(self.graphtabs, className='content-tabs-row')
        ])

    
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
                className='panel_R panel',
            ),
        ], 
        className='layout-mainrow')
    
    @cached_property
    def content_left(self,params=None):
        return dbc.Collapse(
            self.content_main_row, 
            className='layout-leftcol',
            is_open=False
        )
    
    @cached_property
    def content_right(self,params=None):
        return dbc.Collapse(
            dbc.Container(self.graphtab, className='content-belowtabs-row'),
            className='layout-rightcol',
            is_open=True
        )

    @cached_property
    def content(self,params=None):
        return dbc.Container([self.content_left, self.content_right])
        return dbc.Container(
            dbc.Row(
                [
                    dbc.Col(self.content_left),
                    dbc.Col(self.content_right)
                ]
            ), 
            className='panel-comparison-layout layout-belownavbar'
        )
        
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
            dict(label='Left vs. Group 2s', tab_id='map_LR'),
            # dict(label='Group 1', tab_id='map_L'),
            # dict(label='Right', tab_id='map_R'),
        ], tab_level=2, className='graphtabs-container')
        
        tbl_tabs = get_tabs(
            children=[
                dict(label='By member', tab_id='tbl_members'),                
                # dict(label='By arrondissement', tab_id='tbl_arrond'),
            ], 
            tab_level=2, className='graphtabs-container', active_tab='tbl_members'
        )

        analyze_tabs = get_tabs(
            children=[
                # dict(
                #     label='Magnitude of difference',
                #     tab_id='tbl_diff'
                # ),                

                dict(
                    label='By arrondissement', 
                    tab_id='tbl_arrond'
                ),
            ], 
            tab_level=2, 
            className='graphtabs-container'
        )

        graphtabs = get_tabs(
            children=[
                dict(
                    children=map_tabs, 
                    label='Map data', 
                    tab_id='map',
                    tooltip='Map where members lived'
                ),
                dict(children=tbl_tabs, label='View data', tab_id='tbl'),
                dict(children=analyze_tabs, label='Analyze data', tab_id='analyze')
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
            [
                Output(self.content_left, 'is_open'),
                Output(self.content_right, 'style'),
            ],
            Input({"type": "store_desc_btn", "index": ALL}, "n_clicks"),
            State(self.content_left, 'is_open'),
            prevent_initial_callback=True
        )
        #@logger.catch
        def dropdown_the_filters(n_clicks_l, is_open):
            if not any(n_clicks_l): raise PreventUpdate
            if is_open:
                # then shut
                return False, {'width':'100vw'}
            else:
                # then open
                return True, {'width':'50vw'}


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
# @cache_obj.memoize()
def graphtab_cache(serialized_data):
    logger.debug(f'graphtab_cache({serialized_data})')
    tab_ids_1, tab_ids_2, fdL, fdR = unserialize(serialized_data)
    
    # get figure factory
    if not fdL and not fdR:
        # ... @todo change?
        ff = LandmarksFigureFactory()
    elif fdL and not fdR:
        ff = CombinedFigureFactory(fdL, color=LEFT_COLOR)
    elif fdR and not fdL:
        ff = CombinedFigureFactory(fdR, color=RIGHT_COLOR)
    else:
        # both
        ff = ComparisonFigureFactory(fdL, fdR)

    # get view
    viewfunc = determine_view(tab_ids_1, tab_ids_2)

    # return view
    return viewfunc(ff)


def determine_view(tab_ids_1=[], tab_ids_2=[], default=MemberMapView):
    tab_ids_1_set=set(tab_ids_1)
    tab_ids_2_set=set(tab_ids_2)
    logger.debug([tab_ids_1_set, tab_ids_2_set])

    if 'tbl' in tab_ids_1_set and 'tbl_members' in tab_ids_2_set: 
        return MemberTableView

    elif 'analyze' in tab_ids_1_set and 'tbl_arrond' in tab_ids_2_set:
        return ArrondTableView

    elif 'tbl' in tab_ids_1_set:
        return MemberTableView
    
    elif 'map' in tab_ids_1_set:
        return MemberMapView
    
    return default