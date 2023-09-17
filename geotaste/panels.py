from .imports import *
from .views import *


class FilterPanel(FilterCard):
    unfiltered = UNFILTERED

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
            def panel_filter_data_changed(panel_filter_data, *old_filter_data_l):
                if panel_filter_data is None: panel_filter_data={}
                logger.trace(f'[{self.name}] updating my {len(self.store_panel_subcomponents)} subcomponents with my new panel filter data')
                new_filter_data_l = [
                    panel_filter_data
                    for card in self.store_panel_subcomponents    
                ]
                out = new_filter_data_l
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

    @cached_property
    def store_json(self):
        return dcc.Store(id=self.id('store_json'))


    def layout(self, params=None):
        
        return dbc.Container([
            dbc.Container([
                self.panel_L_col, 
                self.panel_R_col,
            ], className='filters-container'),

            dbc.Container([
                # self.mainview_tabs,
                self.mainview,
                self.store,
                self.store_views,
                self.store_json,
                self.table_json,
            ], className='mainview-container')
        ])

    @cached_property
    def store_views(self):
        return dcc.Store(id=self.id('store_views'), data={})
    @cached_property
    def store(self):
        return dcc.Store(id=self.id('store'), data=[])
    @cached_property
    def table_json(self):
        return dcc.Store(id=self.id('table_json'), data='')

    
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
        return dbc.Container([
                self.maintbl_preface_landmarks,
                self.maintbl_preface_members,
                self.maintbl_preface_analysis,
                self.maintbl,
            ],
            id='tblview'
        )

    @cached_property
    def maintbl_preface_landmarks(self):
        return dbc.Collapse(
            [
                html.H4('Data on Landmarks')
            ],
            is_open=True
        )
    
    @cached_property
    def maintbl_preface_members(self):
        return dbc.Collapse(
            [
                html.H4('Data on members')
            ],
            is_open=False
        )
    
    @cached_property
    def maintbl_preface_analysis(self):
        return dbc.Collapse(
            [
                html.H4('Data comparing filters'),
                self.maintbl_preface_analysis_tabs,
                self.maintbl_preface_analysis_content,
            ],
            is_open=False
        )
    
    @cached_property
    def maintbl_preface_analysis_tabs(self):
        return dbc.Tabs([
            dbc.Tab(label='Arrondissement', tab_id='arrond'),
            dbc.Tab(label='Members', tab_id='member'),
            dbc.Tab(label='Authors', tab_id='author'),
            dbc.Tab(label='Books', tab_id='book'),
        ], id='maintbl_preface_analysis_tabs')
    
    @cached_property
    def maintbl_preface_analysis_content(self):
        return dbc.Container()

    def get_maintbl_preface_analysis_content(self, colpref, desc_L, desc_R):
        return dbc.Row([
            dbc.Col([
                html.H5([f'10 most distinctive {"features" if colpref=="all data" else colpref+"s"} for Filter 1 (', self.L.filter_desc,')']),
                dcc.Markdown('\n'.join(desc_L))
            ], className='left-color'),

            dbc.Col([
                html.H5([f'10 most distinctive {"features" if colpref=="all data" else colpref+"s"} for Filter 2 (', self.R.filter_desc,')']),
                dcc.Markdown('\n'.join(desc_R))
            ], className='right-color'),
        ])

    
    
    @cached_property
    def maintbl(self):
        ff = LandmarksFigureFactory()
        dtbl=ff.table()
        return dbc.Container(dtbl,id='maintbl-container')

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

        ### SWITCHING TABS

        @app.callback(
            [
                Output(self.tblview,'style',allow_duplicate=True),
                Output(self.table_json,'data',allow_duplicate=True),

                Output(self.maintbl_preface_landmarks, 'is_open', allow_duplicate=True),
                Output(self.maintbl_preface_members, 'is_open', allow_duplicate=True),
                Output(self.maintbl_preface_analysis, 'is_open', allow_duplicate=True),

                Output('layout-loading-output', 'children', allow_duplicate=True),
            ],
            [
                Input(self.mainview_tabs,'active_tab'),
                Input(self.store,'data'),
                Input(self.maintbl_preface_analysis_tabs, 'active_tab')
            ],
            [
                State(self.tblview,'style'),
            ],
            prevent_initial_call=True
        )
        def switch_tab_simple(active_tab, data, analysis_tab, style_d):
            if style_d is None: style_d={}
            is_open_l = [False, False, False]
            if active_tab!='table':
                ostyle={**style_d, **STYLE_INVIS}
                return [ostyle, dash.no_update] + [dash.no_update for _ in is_open_l] + [True]
            
            # table is active tab
            ostyle={**style_d, **STYLE_VIS}
            fdL,fdR=data if data else ({},{})
            if not fdL and not fdR:
                is_open_l=[True,False,False]
            elif fdL and fdR:
                is_open_l=[False,False,True]
            else:
                is_open_l=[False,True,False]
            
            ojson=get_cached_fig_or_table(serialize([fdL,fdR,'table',analysis_tab]))
            return [ostyle,ojson]+is_open_l+[True]
            
        app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='decompress'
            ),
            Output(self.maintbl, 'children', allow_duplicate=True),
            Input(self.table_json, 'data'),
            prevent_initial_call=True
        )


        ## CHANGING MAP
        @app.callback(
            [
                Output(self.store_json, 'data',allow_duplicate=True),
                Output(self.store,'data',allow_duplicate=True),
                Output('layout-loading-output', 'children', allow_duplicate=True),
                # Output(self.mainview_tabs,'active_tab')
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
            ostore=[Lstore,Rstore]
            logger.debug(ostore)
            with Logwatch('computing figdata on server'):
                newfig_gz_str=get_cached_fig_or_table(serialize([Lstore,Rstore,'map','']))
            
            newfig = from_json_gz_str(newfig_gz_str)
            ofig = go.Figure(data=newfig.data, layout=oldfig['layout'])
            
            logger.debug(f'Assigning a json string of size {sys.getsizeof(newfig_gz_str)} compressed, to self.store_json')
                
            return to_json_gz_str(ofig),ostore,True#,'map'
            

        app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='decompress'
            ),
            Output(self.mainmap, 'figure', allow_duplicate=True),
            Input(self.store_json, 'data'),
            prevent_initial_call=True
        )


        # ## CHANGING DATA TABLE

        # @app.callback(
        #     [
        #         Output(self.maintbl,'children',allow_duplicate=True),
        #         Output('layout-loading-output', 'children', allow_duplicate=True) # spinner
        #     ],
        #     Input(self.store,'data'),
        #     # background=True,
        #     # manager=background_manager,
        #     prevent_initial_call=True
        # )
        # def redo_tbl(data):
        #     with Logwatch('running long callback computation'):
        #         fdL,fdR=data
        #         return get_server_cached_view(serialize([fdL,fdR,'table'])), True


            

        
            

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