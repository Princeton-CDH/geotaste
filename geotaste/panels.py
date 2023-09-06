from .imports import *
from .views import *


class FilterPanel(FilterCard):
    unfiltered = UNFILTERED

    # @cached_property
    # def content(self,params=None):
    #     return dbc.Container([self.store] + super().content.children)
    
    # # @cached_property
    # # def store_desc(self): 
    # #     return html.Span(
    # #         self.unfiltered,
    # #         id=self.id('query_str'), 
    # #         className='store_desc query_str', 
    # #         # placeholder=UNFILTERED, 
    # #         # value='', 
    # #         # style={'color':self.color}
    # #     )

    def describe_filters(self, panel_data):
        return filter_query_str(panel_data, human=True)


    def component_callbacks(self, app):
        super().component_callbacks(app)
        
        # intersect and listen
        if self.store_subcomponents:
            @app.callback(
                Output(self.store, 'data', allow_duplicate=True),
                [
                    Input(card.store, 'data')
                    for card in self.store_subcomponents
                ],
                State(self.store, 'data'),
                prevent_initial_call=True
            )
            def subcomponent_filters_updated(*args):
                filters_d=args[:-1]
                old_data=args[-1]
                intersected_filters=self.intersect_filters(*filters_d)
                if old_data == intersected_filters: raise PreventUpdate # likely a clear
                logger.debug(f'[{self.name}] subcomponent filters updated, triggered by: {ctx.triggered_id}, incoming = {filters_d}, returning {intersected_filters}')
                return intersected_filters

            
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
                #???
                if panel_filter_data is None: panel_filter_data={}
                logger.trace(f'[{self.name}] updating my {len(self.store_panel_subcomponents)} subcomponents with my new panel filter data')
                new_filter_data_l = [
                    # {k:v for k,v in panel_filter_data.items() if k!=card.key}
                    panel_filter_data
                    for card in self.store_panel_subcomponents    
                ]
                out = new_filter_data_l
                # out = [
                #     new if new!=old else dash.no_update
                #     for new,old in zip(new_filter_data_l, old_filter_data_l)
                # ]
                logger.debug(f'sending updates for new store_panel --> {out}')
                return out
            

            

  

class MemberPanel(FilterPanel):
    name='MP'
    figure_factory = CombinedFigureFactory
    desc = 'Members of the library'
    records_name='members'
    # tooltip = 'Filter members of the library by name, date of birth, when active, gender, nationality, and arrondissement'

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
    
    

class BookPanel(FilterPanel):
    name='BP'
    figure_factory = CombinedFigureFactory
    desc = 'Books they borrowed'
    records_name='books'
    # tooltip = 'Filter books borrowed by title, date of publication, genre, author, author gender, author nationality, and the date borrowed'

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
    def author_card(self):
        return AuthorNameCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def author_gender_card(self):
        return AuthorGenderCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def author_nationality_card(self):
        return AuthorNationalityCard(name_context=self.name, **self._kwargs)
    
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
            self.author_card,
            self.author_gender_card,
            self.author_nationality_card,
            self.event_year_card,
            self.event_month_card,
        ]

    @cached_property
    def store_subcomponents(self): return []
    @cached_property
    def graph_subcomponents(self): return []
    
    



class CombinedPanel(FilterPanel):
    name = 'CombinedPanel'
    desc = 'Combined Panel'
    
    @cached_property
    def member_panel(self): 
        return MemberPanel(
            name_context=self.name, 
            desc=self.desc,
            L_or_R=self.L_or_R,
            color=self.color,
            unfiltered=self.unfiltered,
            **self._kwargs
        )

    @cached_property
    def book_panel(self): 
        return BookPanel(
            name_context=self.name, 
            desc=self.desc,
            L_or_R=self.L_or_R,
            color=self.color,
            unfiltered=self.unfiltered,
            **self._kwargs
        )
    

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
    



class LeftPanel(CombinedPanel):
    name='Filter 1'
    desc='Filter 1'
    L_or_R='L'
    color=LEFT_COLOR
    unfiltered=UNFILTERED_L

class RightPanel(CombinedPanel):
    name='Filter 2'
    desc='Filter 2'
    L_or_R='R'
    color=RIGHT_COLOR
    unfiltered=UNFILTERED_R







class ComparisonPanel(BaseComponent):
    figure_factory = ComparisonFigureFactory


    def layout(self, params=None):
        
        return dbc.Container([
            dbc.Container([
                self.panel_L_col, 
                self.panel_R_col,
            ], className='filters-container'),

            dbc.Container([
                self.mainview_tabs,
                self.mainview,
                self.store,
                self.store_views,
            ], className='mainview-container')
        ])

    @cached_property
    def store_views(self):
        return dcc.Store(id=self.id('store_views'), data={})
    @cached_property
    def store(self):
        return dcc.Store(id=self.id('store_views'), data=[])

    
    @cached_property
    def panel_L_col(self):
        return dbc.Container(
            [dbc.Row(self.L.layout())], 
            className='panel_L panel',
            id='panel_L'
        )
    
    @cached_property
    def panel_R_col(self):
        return dbc.Container(
            [dbc.Row(self.R.layout())],
            className='panel_R panel',
            id='panel_R'
        )


    @cached_property
    def subcomponents(self): return (self.L, self.R)

    @cached_property
    def L(self): 
        return LeftPanel()
    
    @cached_property
    def R(self): 
        return RightPanel()
        

    @cached_property
    def mainview_tabs(self):
        return dbc.Tabs(
            [
                dbc.Tab(
                    label='Map', 
                    tab_id='map'
                ),

                dbc.Tab(
                    label='Analysis', 
                    tab_id='table'
                ),
            ],
            id='mainview_tabs',  
            active_tab='map'
        )
    
    @cached_property
    def mapview(self):
        return dbc.Container(self.mainmap,id='mapview')
    
    @cached_property
    def tblview(self):
        return dbc.Container(
            self.maintbl,
            id='tblview'
        )

    @cached_property
    def mainview(self):
        return dbc.Container([
            dbc.Container(self.mapview, id='mapview-container'),
            dbc.Container(self.tblview, id='tblview-container')
        ],
        className='mainview',
        id='mainview'
    )
    
    @cached_property
    def mainmap(self):
        return self.get_mainmap()
    
    def get_mainmap(self, ff=None):
        if ff is None: ff=self.ff()
        ofig = ff.plot_map()
        ofig.update_layout(autosize=True)
        ograph = dcc.Graph(
            figure=go.Figure(ofig), 
            className='comparison_map_graph',
            config={'displayModeBar':False},
            id='mainmap'
        )
        return ograph
    
    @cached_property
    def maintbl(self):
        ff = LandmarksFigureFactory()
        return dbc.Container(
        [
            html.H4('Data'), 
            ff.table() if hasattr(ff,'table') else html.P('??')
        ], 
        className='graphtab padded', 
        id='maintbl'
    )
    
    # def get_mainview(self, fdL={}, fdR={}, viewfunc = MapView):
    #     # get figure factory
    #     num_filters = len([x for x in [fdL,fdR] if x])
    #     # 3 cases
    #     if num_filters==0:
    #         ff = LandmarksFigureFactory()

    #     elif num_filters==1:
    #         if fdL:
    #             ff = CombinedFigureFactory(fdL, color=LEFT_COLOR)
    #         elif fdR:
    #             ff = CombinedFigureFactory(fdR, color=RIGHT_COLOR)

    #     elif num_filters == 2:
    #         ff = ComparisonFigureFactory(fdL, fdR)

    #     # return view
    #     return dbc.Container(
    #         dbc.Tabs(
    #             [
    #                 dbc.Tab(MapView(ff), label='Map', tab_id='map'),
    #                 dbc.Tab(TableView(ff), label='Table', tab_id='table'),
    #             ],
    #             id='mainview_tabs',  
    #             active_tab='map'
    #         ),
    #         className='viewfunc-container'
    #     )

    def ff(self, fdL={}, fdR={}, **kwargs):
        # get figure factory
        num_filters = len([x for x in [fdL,fdR] if x])
        # 3 cases
        if num_filters==0:
            ff = LandmarksFigureFactory()

        elif num_filters==1:
            if fdL:
                ff = CombinedFigureFactory(fdL, color=LEFT_COLOR)
            elif fdR:
                ff = CombinedFigureFactory(fdR, color=RIGHT_COLOR)

        elif num_filters == 2:
            ff = ComparisonFigureFactory(fdL, fdR)

        return ff

    def get_mainmap_data(self, fdL={}, fdR={}):
        if fdL or fdR:
            odata=[]
            if fdL: odata.extend(self.ff(fdL=fdL).plot_map().data)
            if fdR: odata.extend(self.ff(fdR=fdR).plot_map().data)
        else:
            odata = self.ff().plot_map().data
        return odata


    def component_callbacks(self, app):
        super().component_callbacks(app)

        # @app.callback(
        #     Output('tblview-container','style',allow_duplicate=True),
        #     [
        #         Input(self.L.showhide_btn, "n_clicks"),
        #         Input(self.L.header_btn, 'n_clicks'),
        #         Input(self.R.showhide_btn, "n_clicks"),
        #         Input(self.R.header_btn, 'n_clicks'),
        #         Input(self.L.body, 'is_open'),
        #         Input(self.R.body, 'is_open'),
        #     ],
        #     [
        #         State('tblview-container','style'),
        #     ],
        #     prevent_initial_call=True
        # )
        # def resize_tbl_view(clk1,clk2,clk3,clk4, L_open,R_open, style_d):
        #     logger.debug([clk1,clk2,clk3,clk4, L_open,R_open, style_d])
        #     if style_d is None: style_d={}
        #     style_d['padding-left']=f'{501 if R_open else (251 if L_open else 0)}px'
        #     logger.debug(f'--> {style_d}')
        #     return style_d
        


        ## CHANGING DATA

        @app.callback(
            Output(self.maintbl,'children',allow_duplicate=True),
            Input(self.store,'data'),
            background=True,
            manager=background_manager,
            prevent_initial_call=True
        )
        def redo_tbl(data):
            with Logwatch('running long callback computation'):
                fdL,fdR=data
                return get_server_cached_view(serialize([fdL,fdR,'table']))

        @app.callback(
            [
                Output(self.mainmap,'figure',allow_duplicate=True),
                Output(self.maintbl,'children',allow_duplicate=True),
                Output(self.store,'data'),
            ],
            [
                Input(self.L.store, 'data'),
                Input(self.R.store, 'data'),
                # Input(self.mainview_tabs, 'active_tab')
            ],
            [
                State(self.mainmap,'figure'),
            ],
            prevent_initial_call=True
        )
        def update_LR_data(Lstore, Rstore, oldfig):
            logger.debug([Lstore,Rstore])
            with Logwatch('computing figdata on server'):
                newfig=get_server_cached_view(serialize([Lstore,Rstore,'map']))
                ofig = newfig if not oldfig else {'data':newfig.data, 'layout':oldfig['layout']}
                # otbl = get_server_cached_view(serialize([Lstore,Rstore,'table']))
                otbl='loading...'
                # logger.debug(tbldata)
                return ofig,otbl,[Lstore,Rstore]


            
            
        ### SWITCHING TABS

        @app.callback(
            Output('tblview','style',allow_duplicate=True),
            Input(self.mainview_tabs,'active_tab'),
            State('tblview','style'),
            prevent_initial_call=True
        )
        def switch_tab_simple(active_tab, style_d):
            if style_d is None: style_d={}
            return {**style_d, **(STYLE_INVIS if active_tab=='map' else STYLE_VIS)}


        # @app.callback(
        #     [
        #         Output(self.mapview,'style',allow_duplicate=True),
        #         Output(self.tblview,'style',allow_duplicate=True)
        #     ],
        #     [
        #         Input(self.mainview_tabs, 'active_tab')
        #     ],
        #     [
        #         State(self.mainmap,'figure'),
        #         State(self.mapview,'style'),
        #         State(self.tblview,'style'),
        #         State(self.L.body, "is_open"),
        #         State(self.R.body, 'is_open'),
        #     ],
        #     prevent_initial_call=True
        # )
        # def change_tab(active_tab, oldfig, imap_style, itbl_style, L_open, R_open):
        #     if imap_style is None: imap_style={}
        #     if itbl_style is None: itbl_style={}
        #     logger.debug([active_tab, imap_style, itbl_style, L_open, R_open])
        #     if active_tab=='map':
        #         ofig_style = {**imap_style, **STYLE_VIS}
        #         otbl_style = {**itbl_style, **STYLE_INVIS}
        #     else:
        #         ofig_style = {**imap_style, **STYLE_INVIS}
        #         otbl_style = {**itbl_style, **STYLE_VIS}

        #     otbl_style['left']=f'{500 if R_open else (250 if L_open else 0)}px'

        #     out = ofig_style, otbl_style
        #     logger.debug(f'--> {out}')
        #     return out


        # @app.callback(
        #     [
        #         Output(self.mainmap, 'figure',allow_duplicate=True),
        #         Output(self.maintbl,'children',allow_duplicate=True),
        #         Output(self.store_views, 'data',allow_duplicate=True)
        #     ],
        #     [
        #         Input(self.L.store, 'data'),
        #         Input(self.R.store, 'data'),
        #     ],
        #     [
        #         State(self.mainmap,'figure'),
        #         State(self.store_views, 'data')
        #     ],
        #     prevent_initial_call=True
        # )
        # def update_LR_data(Lstore, Rstore, oldfig, oldviews):
        #     if oldviews is None: oldviews = {}
        #     with Logwatch('returning informations'):
        #         args_id=serialize([Lstore,Rstore])
        #         if args_id in oldviews:
        #             logger.debug(f'{args_id} found in oldviews!')
        #             return oldviews[args_id] + [dash.no_update]
                
        #         else:
        #             ofigdata,otbl = get_cached_views(args_id)
        #             oldviews[args_id] = [ofigdata,otbl]
        #             ofig = self.get_updated_fig(ofigdata,oldfig)
        #             return [ofig,otbl,oldviews]



    # def component_callbacks(self, app):
    #     super().component_callbacks(app)

    #     @app.callback(
    #         [
    #             Output(self.content_left, 'is_open', allow_duplicate=True),                      # dropdowns open
    #             # Output(self.storedesc_R_col, 'style', allow_duplicate=True),                     # whether right filter button visible
    #             Output(self.panel_R_col, 'style', allow_duplicate=True),                         # whether right filter panel visible
    #             Output(self.graphtab, 'children', allow_duplicate=True),   # actual content
    #             Output('layout-loading', 'children') # spinner
    #         ],
    #         [
    #             Input(self.L.store, 'data'),                               # any changes in left filter
    #             Input(self.R.store, 'data'),                               # any in right filter
    #             Input(self.storedesc_L_btn, "n_clicks"),
    #             Input(self.storedesc_R_btn, "n_clicks"),
    #             Input(self.graphtabs, 'active_tab')
    #         ],
    #         [
    #             State(self.content_left, 'is_open'),
    #             State(self.L.store, 'data'),
    #             State(self.R.store, 'data'),

    #         ],
    #         prevent_initial_call=True
    #     )
    #     def determine_dropdown_and_view(
    #             fdL, 
    #             fdR, 
    #             storedesc_L_clicked, 
    #             storedesc_R_clicked, 
    #             active_tab, 
    #             filter_dropdown_open_now,
    #             old_fdL,
    #             old_fdR,
    #             ):
    #         input_ids = [
    #             self.L.store.id, 
    #             self.R.store.id, 
    #             self.storedesc_L_btn.id, 
    #             self.storedesc_R_btn.id, 
    #             self.graphtabs.id
    #         ]
    #         outs = [
    #             dash.no_update,  # both dropdown vis
    #             # dash.no_update,  # right vis
    #             # dash.no_update,  # right vis
    #             # STYLE_VIS if fdL and storedesc_R_clicked else STYLE_VIS,
    #             # STYLE_VIS,
    #             STYLE_VIS if fdL and storedesc_R_clicked else STYLE_INVIS,
    #             dash.no_update   # content,
    #         ]
            
    #         logger.debug(ctx.triggered)
    #         logger.debug(input_ids)

    #         # if we clicked the Left or Right top Filter tab button
    #         if ctx.triggered_id in {self.storedesc_L_btn.id, self.storedesc_R_btn.id}:
    #             if storedesc_R_clicked!=1:
    #                 outs[0]=not filter_dropdown_open_now

    #         # if the tab changed -- or the filters changed
    #         elif ctx.triggered_id in {self.graphtabs.id, self.L.store.id, self.R.store.id}:

    #             # make sure change actually happened?
    #             args = [[active_tab],[],fdL,fdR]
    #             logger.debug(['switchtab'] + args)
    #             logger.debug([fdL, old_fdL])
    #             logger.debug([fdR, old_fdR])
    #             serialized_data = serialize(args)
    #             outs[-1] = graphtab_cache(serialized_data)

    #             # also collapse dropdowns if tab changed
    #             # if ctx.triggered_id == self.graphtabs.id:
    #                 # outs[0] = False
            
    #         # logger.debug(outs)
    #         return outs + [True]



        
            

# @cache
# @cache_obj.memoize()
def graphtab_cache(serialized_data):
    logger.trace(f'graphtab_cache({serialized_data})')
    tab_ids_1, tab_ids_2, fdL, fdR = unserialize(serialized_data)
    
    # get figure factory
    if not fdL and not fdR:
        # ... @todo change?
        ff = LandmarksFigureFactory()
        num_filters = 0
        # ff = CombinedFigureFactory(fdL, color=LEFT_COLOR)
        # num_filters = 1
    elif fdL and not fdR:
        ff = CombinedFigureFactory(fdL, color=LEFT_COLOR)
        num_filters = 1
    elif fdR and not fdL:
        ff = CombinedFigureFactory(fdR, color=RIGHT_COLOR)
        num_filters = 1
    else:
        # both
        ff = ComparisonFigureFactory(fdL, fdR)
        num_filters = 2

    # get view
    viewfunc = determine_view(tab_ids_1, tab_ids_2, num_filters=num_filters)

    # return view
    return dbc.Container(viewfunc(ff), className='viewfunc-container')


def determine_view(tab_ids_1=[], tab_ids_2=[], default=MapView, num_filters=1):
    tab_ids_1_set=set(tab_ids_1)
    if 'data' in tab_ids_1_set:
        return MemberTableView
    elif 'map' in tab_ids_1_set:
        return MapView
    elif 'analysis' in tab_ids_1_set:
        return AnalysisTableView if num_filters>1 else MemberTableView
    
    return default