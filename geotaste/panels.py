from .imports import *
from urllib.parse import urlencode, parse_qs


class FilterPanel(FilterCard):
    unfiltered = UNFILTERED

    def describe_filters(self, panel_data):
        """Describes the filters applied to the panel data.
        
        Args:
            panel_data (list): The panel data to describe the filters for.
        
        Returns:
            str: The filter query string.
        """
        return filter_query_str(panel_data, human=True)

    
    def component_callbacks(self, app):
        """This function sets up the component callbacks for the given app.
        
        Args:
            app: The Dash app object.
        
        Returns:
            None
        """
        
        # run parents
        super().component_callbacks(app)
        
        # intersect and listen
        if self.store_subcomponents:
            @app.callback(
                [
                    Output(card.store_panel, 'data', allow_duplicate=True)
                    for card in self.store_panel_subcomponents
                ] + [Output(self.store, 'data')],
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

                # out
                panel_filter_data = intersected_filters
                new_filter_data_l = [
                    # (panel_filter_data if card.store.id != ctx.triggered_id else dash.no_update)
                    panel_filter_data  # resets selections on clears better this way to update even the component that triggered the panel
                    for card in self.store_panel_subcomponents    
                ]
                out = new_filter_data_l + [panel_filter_data]
                logger.debug(f'sending updates for new store_panel --> {out}')
                return out
            
            

  

class MemberPanel(FilterPanel):
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
    
    

class BookPanel(FilterPanel):
    name='BP'
    figure_factory = CombinedFigureFactory
    desc = 'Books they borrowed'
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
        """Creates a member panel object.
        
        Args:
            self (object): The current instance of the class.
            
        Returns:
            MemberPanel: A member panel object with the specified attributes.
        """
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
        """Creates a BookPanel object with the specified parameters.
        
        Args:
            self (object): The current instance of the class.
            
        Returns:
            BookPanel: A BookPanel object with the specified parameters.
        """
        
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
        """Returns a list of cards that have a specific attribute.
        
        Args:
            attrname (str): The name of the attribute to check for.
        
        Returns:
            list: A list of cards that have the specified attribute.
        """
        
        return [
            card
            for panel in self.subcomponents
            for card in panel.subcomponents
            if hasattr(card,attrname)
        ]
    



class LeftPanel(CombinedPanel):
    name='Filter_1'
    desc='Filter 1'
    L_or_R='L'
    color=LEFT_COLOR
    unfiltered=UNFILTERED_L

class RightPanel(CombinedPanel):
    name='Filter_2'
    desc='Filter 2'
    L_or_R='R'
    color=RIGHT_COLOR
    unfiltered=UNFILTERED_R






class ComparisonPanel(BaseComponent):
    """A class used to represent a Comparison Panel that is a child of the Base Component"""

    figure_factory = ComparisonFigureFactory

    @cached_property
    def store_json(self):
        """Property method to represent a store giving the ability to store JSON objects

        Returns:
            dcc.Store: The dash core component Store object
        """
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
                self.store_json,
                self.table_json,
                self.test_suite,
                self.app_begun
            ], className='mainview-container')


        ])
    
    @cached_property
    def test_suite(self):
        return dbc.Container([self.test_suite_btn1, self.test_suite_btn2, self.test_suite_btn3], className='test_suite')
    
    @cached_property
    def test_suite_btn1(self):
        return dbc.Button(
            '',
            color='link',
            n_clicks=0,
            id='test_suite_btn1',
            className='test_suite_btn'
        )
    
    @cached_property
    def test_suite_btn2(self):
        return dbc.Button('',color='link',n_clicks=0,id='test_suite_btn2',className='test_suite_btn')
    
    @cached_property
    def test_suite_btn3(self):
        return dbc.Button('',color='link',n_clicks=0,id='test_suite_btn3',className='test_suite_btn')
        

    @cached_property
    def store(self):
        """Stores data in a Dash Core Component Store.
        
        Args:
            self: The instance of the class.
        
        Returns:
            dcc.Store: [left filter data, right filter data]
        """
        return dcc.Store(id=self.id('store'), data=[])
    @cached_property
    def table_json(self):
        """Returns a Dash Core Component Store object with an empty JSON string as the initial data.
        
        Args:
            self (object): The instance of the class.
        
        Returns:
            dcc.Store: A Dash Core Component Store object.
        """
        
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
        """Creates a Tabs component for the main view.
        
        Returns:
            dbc.Tabs: The Tabs component.    
        """
        return dbc.Tabs(
            [
                dbc.Tab(
                    label='Map', 
                    tab_id='map',
                    id='tab_map'
                ),

                dbc.Tab(
                    label='Analysis', 
                    tab_id='table',
                    id='tab_table'
                ),
            ],
            id='mainview_tabs',  
            active_tab='map'
        )
    
    @cached_property
    def mapview(self):
        """Returns a Container component with the main map view.
        
        Returns:
            dbc.Container: A Container component with the main map view.
        """
        
        return dbc.Container(self.mainmap,id='mapview')
    
    @cached_property
    def tblview(self):
        """Returns a Dash Bootstrap Components (dbc) Container containing multiple dbc.Collapse components for the various parts of the tblview.
        
            Returns:
                dbc.Container: object containing the main table preface landmarks, main table preface members, 
                     main table preface analysis, and the main table itself.
        """
        
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
        """Returns a Collapse component containing a heading for the data on landmarks.
        
            Returns:
                dbc.Collapse: A Collapse component containing a heading and any other introductory information for the data on landmarks.
        """
        
        return dbc.Collapse(
            [
                html.H4('Data on landmarks')
            ],
            is_open=True
        )
    
    @cached_property
    def maintbl_preface_members(self):
        """Returns a Collapse component containing a preface for the main table of members. This function creates a Collapse component from the `dash_bootstrap_components.Collapse` class. The Collapse component is used to hide or show content based on user interaction. The preface for the main table of members is displayed inside the Collapse component.
        
            Returns:
                dbc.Collapse: The Collapse component.
        """
        
        return dbc.Collapse(
            [
                html.H4('Data on members')
            ],
            is_open=False
        )
    
    @cached_property
    def app_begun(self): return dcc.Store(id=self.id('app_begun'), data=None)
    
    @cached_property
    def maintbl_preface_analysis(self):
        """Returns a Collapse component containing the preface analysis for the main table. This function creates a Collapse component that includes a heading, tabs, and content for the preface analysis of the main table. The Collapse component is initially closed.
        
            Returns:
                dbc.Collapse: A Collapse component containing the preface analysis for the main table.
        """
        
        return dbc.Collapse(
            [
                html.H4('Data comparing filters'),
                self.maintbl_preface_analysis_tabs,
            ],
            is_open=False
        )
    
    @cached_property
    def maintbl_preface_analysis_tabs(self):
        """Creates a set of tabs for the main table preface analysis.
        
        Returns:
            dbc.Tabs: A set of tabs for the main table preface analysis.
        """
        
        return dbc.Tabs([
            dbc.Tab(label='Arrondissement', tab_id='arrond'),
            dbc.Tab(label='Members', tab_id='member'),
            dbc.Tab(label='Authors', tab_id='author'),
            dbc.Tab(label='Books', tab_id='book'),
        ], id='maintbl_preface_analysis_tabs', active_tab='arrond')
    
    @cached_property
    def maintbl(self):
        """Creates and returns a container with initially a table of landmarks.
        
        Returns:
            dbc.Container: A container with initially the table of landmarks.
        """
        
        ff = LandmarksFigureFactory()
        dtbl=ff.table()
        return dbc.Container(dtbl,id='maintbl-container')

    @cached_property
    def mainview(self):
        """Returns a Container component containing the mapview and tblview components.
            
        Returns:
            A dbc.Container component containing the mapview and tblview components.            
        """
        
        return dbc.Container([
            dbc.Container(self.mapview, id='mapview-container'),
            dbc.Container(self.tblview, id='tblview-container')
        ],
        className='mainview',
        id='mainview'
    )
    
    @cached_property
    def mainmap(self):
        """Returns the main map.
        
        Returns:
            dcc.Graph: The main map Graph component
        """
        return self.get_mainmap()
    
    def get_mainmap(self, ff=None):
        """Get the main map.
        
        Args:
            ff (optional): The figure factory object. Defaults to None.
        
        Returns:
            dcc.Graph: The main map graph.
        """
        
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
        """Creates a figure factory based on the given filters.
        
        Args:
            fdL (dict, optional): Filter dictionary for the left side. Defaults to {}.
            fdR (dict, optional): Filter dictionary for the right side. Defaults to {}.
            **kwargs: Additional keyword arguments.
        
        Returns:
            FigureFactory: The created figure factory.
        """
        
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


    def component_callbacks(self, app):
        """Callback functions for component interactions in the app:
    * switch_tab_simple -> clientside -> table
    * update_LR_data -> cleintside -> figure
        
        Args:
            app: The Dash app object.
        
        Returns:
            None
        """
        

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
            
            ojson=get_cached_fig_or_table(serialize([fdL,fdR,'table',analysis_tab,{}]))
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
                newfig_gz_str=get_cached_fig_or_table(serialize([Lstore,Rstore,'map','',{}]))
            
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



        ### test funcs
        @app.callback(
            Output(self.L.store, 'data', allow_duplicate=True),
            Input(self.test_suite_btn1, 'n_clicks'),
            prevent_initial_call=True
         )
        def test_suite_btn1_onclick(n_clicks):
            return {'member_nationalities':['France']}
        
        @app.callback(
            Output(self.R.store, 'data', allow_duplicate=True),
            Input(self.test_suite_btn2, 'n_clicks'),
            prevent_initial_call=True
         )
        def test_suite_btn2_onclick(n_clicks):
            return {'member_nationalities':['United States']}


        @app.callback(
            Output(self.R.store, 'data', allow_duplicate=True),
            Input(self.test_suite_btn3, 'n_clicks'),
            prevent_initial_call=True
         )
        def test_suite_btn3_onclick(n_clicks):
            return {}


        @app.callback(
            Output('url-output', 'search', allow_duplicate=True),
            [
                Input(self.L.store, 'data'),
                Input(self.R.store, 'data'),
                Input(self.mainview_tabs, 'active_tab'),
                Input(self.maintbl_preface_analysis_tabs, 'active_tab'),
                Input(self.mainmap, 'relayoutData')
            ],
            prevent_initial_call=True
        )
        def track_state(fdL, fdR, tab, tab2, figdat):
            logger.debug(f'triggered by {ctx.triggered_id}')
            state = {}
            for k,v in fdL.items(): state[k]=rejoin_sep(v)
            for k,v in fdR.items(): state[k+'2']=rejoin_sep(v)
            state['tab']=tab
            state['tab2']=tab2
            if figdat:
                state['lat']=round(figdat.get('mapbox.center',{}).get('lat',0), 5)
                state['lon']=round(figdat.get('mapbox.center',{}).get('lon',0), 5)
                state['zoom']=round(figdat.get('mapbox.zoom',0), 5)
                state['bearing']=round(figdat.get('mapbox.bearing',0), 5)
                state['pitch']=round(figdat.get('mapbox.pitch',0), 5)
            
            state = {k:v for k,v in state.items() if v and DEFAULT_STATE.get(k)!=v}
            if not state: return ''
            ostr=f'?{urlencode(state)}'
            return ostr
                





        @app.callback(
            [
                Output(self.L.store, 'data',allow_duplicate=True),
                Output(self.R.store, 'data',allow_duplicate=True),
                Output(self.mainview_tabs, 'active_tab',allow_duplicate=True),
                Output(self.maintbl_preface_analysis_tabs, 'active_tab',allow_duplicate=True),
                Output(self.mainmap, 'figure',allow_duplicate=True),
                Output(self.app_begun, 'data',allow_duplicate=True),
                Output('welcome-modal', 'is_open')
            ],
            Input('url-input','search'),
            [
                State(self.app_begun, 'data'),
                State(self.mainmap, 'figure'),
            ],
            prevent_initial_call=True
        )
        def load_query_param(searchstr, app_begun, figdat):
            if app_begun: raise PreventUpdate
            searchstrx=searchstr[1:]
            if not searchstrx: raise PreventUpdate
            params = parse_qs(searchstrx)
            logger.debug(params)
            fdL, fdR, tab, tab2, mapd = {}, {}, 'map', 'arrond', {}

            for k,v in list(params.items()):
                if k=='tab':
                    tab=v[0]
                elif k=='tab2':
                    tab2=v[0]
                elif k.endswith('2'):
                    fdR[k[:-1]]=[ensure_int(y,return_orig=True) for y in v[0].split('_')]
                elif '_' in k:
                    fdL[k]=[ensure_int(y,return_orig=True) for y in v[0].split('_')]
                else:
                    mapd[k]=float(v[0])
            
            if 'lat' in mapd: figdat['layout']['mapbox']['center']['lat'] = mapd['lat']
            if 'lon' in mapd: figdat['layout']['mapbox']['center']['lon'] = mapd['lon']
            if 'zoom' in mapd: figdat['layout']['mapbox']['zoom'] = mapd['zoom']
            if 'bearing' in mapd: figdat['layout']['mapbox']['bearing'] = mapd['bearing']
            if 'pitch' in mapd: figdat['layout']['mapbox']['pitch'] = mapd['pitch']
            out = [fdL, fdR, tab, tab2, figdat, True, False]
            logger.debug(f'--> {out[:4] + out[5:]}')
            return out
            
