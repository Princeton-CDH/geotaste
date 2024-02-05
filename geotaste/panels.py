from .imports import *
from urllib.parse import urlencode


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
            logger.warning(f'{self} -> {self.store_subcomponents}')
            app.clientside_callback(ClientsideFunction(
                namespace='clientside',
                function_name='intersect_subcomponent_filters'),
                                    Output(self.store, 'data'), [
                                        Input(card.store, 'data')
                                        for card in self.store_subcomponents
                                    ],
                                    State(self.store, 'data'),
                                    prevent_initial_call=True)

            app.clientside_callback(
                """
                function(panel_data) {
                    // """ + self.name + """
                    console.log(""" + repr(self.name) +
                """, "sending",panel_data,"to",""" + json.dumps(
                    [card.name
                     for card in self.store_panel_subcomponents]) + """);
                    return new Array(""" +
                str(len(self.store_panel_subcomponents)) +
                """).fill(panel_data);
                }
                """, [
                    Output(card.store_panel, 'data', allow_duplicate=True)
                    for card in self.store_panel_subcomponents
                ],
                Input(self.store, 'data'),
                prevent_initial_call=True)

            app.clientside_callback(
                """
                function(clicks) {
                    res = new Array(""" +
                (str(len(self.store_subcomponents))) + """).fill({});
                    console.log('clearing',""" + repr(self.name) + """,res);
                    return res;
                }
                """, [
                    Output(card.store, 'data', allow_duplicate=True)
                    for card in self.store_subcomponents
                ],
                Input(self.button_clear, 'n_clicks'),
                prevent_initial_call=True)

            # if not isinstance(self, ComparisonPanel):
            app.clientside_callback(
                """
                function(data) {
                    console.log('incoming data',data);
                    let keys = [""" +
                ", ".join(f'{repr(card.key)}'
                          for card in self.store_subcomponents) + """];
                    return process_incoming_data(data,keys);
                }
                """, [
                              Output(card.store, 'data', allow_duplicate=True)
                              for card in self.store_subcomponents
                          ],
                Input(self.store_incoming, 'data'),
                prevent_initial_call=True)


class MemberPanel(FilterPanel):
    name = 'MP'
    figure_factory = CombinedFigureFactory
    desc = 'Members of the library'
    records_name = 'members'

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
    def store_subcomponents(self):
        return []

    @cached_property
    def graph_subcomponents(self):
        return []


class BookPanel(FilterPanel):
    name = 'BP'
    figure_factory = CombinedFigureFactory
    desc = 'Books they borrowed'
    records_name = 'books'

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
    def store_subcomponents(self):
        return []

    @cached_property
    def graph_subcomponents(self):
        return []


class CombinedPanel(FilterPanel):
    name = 'CombinedPanel'
    desc = 'Combined Panel'
    L_or_R = 'X'
    color = None

    @cached_property
    def member_panel(self):
        """Creates a member panel object.
        
        Args:
            self (object): The current instance of the class.
            
        Returns:
            MemberPanel: A member panel object with the specified attributes.
        """
        return MemberPanel(name_context=self.name,
                           desc=self.desc,
                           L_or_R=self.L_or_R,
                           color=self.color,
                           unfiltered=self.unfiltered,
                           **self._kwargs)

    @cached_property
    def book_panel(self):
        """Creates a BookPanel object with the specified parameters.
        
        Args:
            self (object): The current instance of the class.
            
        Returns:
            BookPanel: A BookPanel object with the specified parameters.
        """

        return BookPanel(name_context=self.name,
                         desc=self.desc,
                         L_or_R=self.L_or_R,
                         color=self.color,
                         unfiltered=self.unfiltered,
                         **self._kwargs)

    @cached_property
    def subcomponents(self):
        return [
            self.member_panel,
            self.book_panel,
        ]

    def cards_with_attr(self, attrname: str):
        """Returns a list of cards that have a specific attribute.
        
        Args:
            attrname (str): The name of the attribute to check for.
        
        Returns:
            list: A list of cards that have the specified attribute.
        """

        return [
            card for panel in self.subcomponents
            for card in panel.subcomponents if hasattr(card, attrname)
        ]


class LeftPanel(CombinedPanel):
    name = 'Filter_1'
    desc = 'Filter 1'
    L_or_R = 'L'
    color = LEFT_COLOR
    unfiltered = UNFILTERED_L
    show_contrast_btn = True
    contrast_btn_msg = '[cf. 2]'


class RightPanel(CombinedPanel):
    name = 'Filter_2'
    desc = 'Filter 2'
    L_or_R = 'R'
    color = RIGHT_COLOR
    unfiltered = UNFILTERED_R
    show_contrast_btn = True
    contrast_btn_msg = '[cf. 1]'


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
            ],
                          className='filters-container'),
            dbc.Container(
                [
                    # self.mainview_tabs,
                    self.mainview,
                    self.store,
                    self.store_json,
                    self.store_markers_L,
                    self.store_markers_R,
                    self.table_json,
                    self.test_suite,
                    self.test_suite_btn,
                    self.app_begun
                ],
                className='mainview-container')
        ])

    @cached_property
    def store_markers_L(self):
        return dcc.Store(id=self.id('store_markers_L'), data={})

    @cached_property
    def store_markers_R(self):
        return dcc.Store(id=self.id('store_markers_R'), data={})

    @cached_property
    def test_suite(self, num_btn=6):
        return dbc.Collapse(
            [self.get_test_suite_btn(suffix=f'{i+1}') for i in range(num_btn)],
            className='test_suite',
            id='test_suite',
            is_open=False)

    @cached_property
    def test_suite_btn(self):
        return self.get_test_suite_btn()

    def get_test_suite_btn(self, suffix=''):
        return dbc.Button('',
                          color='link',
                          n_clicks=0,
                          id='test_suite_btn' + suffix,
                          className='test_suite_btn')

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
        return dbc.Container([dbc.Row(self.L.layout())],
                             className='panel_L panel',
                             id='panel_L')

    @cached_property
    def panel_R_col(self):
        return dbc.Container([dbc.Row(self.R.layout())],
                             className='panel_R panel',
                             id='panel_R')

    @cached_property
    def subcomponents(self):
        return (self.L, self.R)

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
        return dbc.Tabs([
            dbc.Tab(label='Map', tab_id='map', id='tab_map'),
            dbc.Tab(label='Analysis', tab_id='table', id='tab_table'),
        ],
                        id='mainview_tabs',
                        active_tab='map')

    @cached_property
    def mapview(self):
        """Returns a Container component with the main map view.
        
        Returns:
            dbc.Container: A Container component with the main map view.
        """

        return dbc.Container(self.mainmap, id='mapview')

    @cached_property
    def tblview(self):
        """Returns a Dash Bootstrap Components (dbc) Container containing multiple dbc.Collapse components for the various parts of the tblview.
        
            Returns:
                dbc.Container: object containing the main table preface landmarks, main table preface members, 
                     main table preface analysis, and the main table itself.
        """

        return dbc.Container([
            # self.maintbl_preface_landmarks,
            # self.maintbl_preface_members,
            self.maintbl_preface_analysis,
            self.maintbl,
        ],
                             id='tblview')

    @cached_property
    def maintbl_preface_landmarks(self):
        """Returns a Collapse component containing a heading for the data on landmarks.
        
            Returns:
                dbc.Collapse: A Collapse component containing a heading and any other introductory information for the data on landmarks.
        """

        return dbc.Collapse([html.H4('Data on landmarks')], is_open=True)

    @cached_property
    def maintbl_preface_members(self):
        """Returns a Collapse component containing a preface for the main table of members. This function creates a Collapse component from the `dash_bootstrap_components.Collapse` class. The Collapse component is used to hide or show content based on user interaction. The preface for the main table of members is displayed inside the Collapse component.
        
            Returns:
                dbc.Collapse: The Collapse component.
        """

        return dbc.Collapse([html.H4('Data on members')], is_open=False)

    @cached_property
    def app_begun(self):
        return dcc.Store(id=self.id('app_begun'), data=None)

    @cached_property
    def maintbl_preface_analysis(self):
        """Returns a Collapse component containing the preface analysis for the main table. This function creates a Collapse component that includes a heading, tabs, and content for the preface analysis of the main table. The Collapse component is initially closed.
        
            Returns:
                dbc.Collapse: A Collapse component containing the preface analysis for the main table.
        """

        return dbc.Collapse([
            self.maintbl_preface_analysis_title,
            self.maintbl_preface_analysis_tabs,
        ],
                            is_open=True)

    @cached_property
    def maintbl_preface_analysis_title(self):
        return html.H4('Data')

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
        ],
                        id='maintbl_preface_analysis_tabs',
                        active_tab='arrond')

    @cached_property
    def maintbl(self):
        """Creates and returns a container with initially a table of landmarks.
        
        Returns:
            dbc.Container: A container with initially the table of landmarks.
        """

        ff = LandmarksFigureFactory()
        dtbl = ff.table()
        return dbc.Container(dtbl, id='maintbl-container')

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
                             id='mainview')

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

        if ff is None: ff = self.ff()
        dlMap = ff.plot_map()
        return dlMap

    def ff(self, fdL={}, fdR={}, landmarks=True,**kwargs):
        """Creates a figure factory based on the given filters.
        
        Args:
            fdL (dict, optional): Filter dictionary for the left side. Defaults to {}.
            fdR (dict, optional): Filter dictionary for the right side. Defaults to {}.
            **kwargs: Additional keyword arguments.
        
        Returns:
            FigureFactory: The created figure factory.
        """

        # get figure factory
        num_filters = len([x for x in [fdL, fdR] if x])
        # 3 cases
        if num_filters == 0 and landmarks:
            ff = LandmarksFigureFactory()

        elif num_filters == 1:
            if fdL:
                ff = CombinedFigureFactory(fdL, color=LEFT_COLOR)
            elif fdR:
                ff = CombinedFigureFactory(fdR, color=RIGHT_COLOR)

        elif num_filters == 2:
            ff = ComparisonFigureFactory(fdL, fdR)

        else:
            ff = CombinedFigureFactory()

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

        app.clientside_callback(
            ClientsideFunction(namespace='clientside',
                               function_name='intersect_and_negate'),
            Output(self.L.store_incoming, 'data', allow_duplicate=True),
            Input(self.L.contrast_btn, 'n_clicks'),
            [State(card.store, 'data') for card in self.R.store_subcomponents],
            prevent_initial_call=True)

        app.clientside_callback(
            ClientsideFunction(namespace='clientside',
                               function_name='intersect_and_negate'),
            Output(self.R.store_incoming, 'data', allow_duplicate=True),
            Input(self.R.contrast_btn, 'n_clicks'),
            [State(card.store, 'data') for card in self.L.store_subcomponents],
            prevent_initial_call=True)


        ### SWITCHING TABS

        @app.callback(
            [
                Output(self.tblview,'style',allow_duplicate=True),
                Output(self.table_json,'data',allow_duplicate=True),
                Output('layout-loading-output', 'children', allow_duplicate=True),
                Output(self.maintbl_preface_analysis_title, 'children', allow_duplicate=True)
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
            ostyle={**style_d, **STYLE_INVIS}
            if active_tab!='table': 
                return (ostyle, dash.no_update, dash.no_update,dash.no_update)
            
            # table is active tab
            ostyle={**style_d, **STYLE_VIS}
            fdL,fdR=data if data else ({},{})
            ojson=get_cached_fig_or_table(serialize([fdL,fdR,'table',analysis_tab,{}]))

            if fdL and fdR:
                title='Data comparing filters'
            elif fdL:
                title='Data on Filter 1'
            elif fdR:
                title='Data on Filter 2'
            else:
                title="Data"

            return [ostyle,ojson,"",title]
            
        app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='decompress_json_gz',
            ),
            Output(self.maintbl, 'children', allow_duplicate=True),
            Input(self.table_json, 'data'),
            prevent_initial_call=True,
        )

        app.clientside_callback("""
            function(Lstore, Rstore) {
                let ostore=[Lstore,Rstore];
                //let out = [ostore, true];
                let out = ostore;
                console.log('->',out);
                return out;
            }
            """,
            Output(self.store, 'data', allow_duplicate=True),
            # Output('layout-loading-output', 'children', allow_duplicate=True),
            [
                Input(self.L.store, 'data'),
                Input(self.R.store, 'data'),
            ],
            prevent_initial_call=True
        )

        @app.callback(
            [
                Output(self.store_markers_L, 'data'),
                Output('layout-loading-output', 'children', allow_duplicate=True),
            ],
            Input(self.L.store, 'data'),
            prevent_initial_call=True
        )
        def put_markers_L(data):
            if not data: return [],""
            return list(self.ff(fdL=data).df_dwellings.index),""

        @app.callback(
                [
                    Output(self.store_markers_R, 'data'),
                    Output('layout-loading-output', 'children', allow_duplicate=True),
                ],
                Input(self.R.store, 'data'),
                prevent_initial_call=True
        )
        def put_markers_R(data):
            if not data: return [],""
            return list(self.ff(fdR=data).df_dwellings.index),""

        app.clientside_callback("""
            function(dwellings) {
                return get_dwelling_markers(dwellings, "L");
            }
            """,
                                Output("featuregroup-markers",
                                       "children",
                                       allow_duplicate=True),
                                Input(self.store_markers_L, 'data'),
                                prevent_initial_call=True)

        app.clientside_callback("""
            function(dwellings) {
                return get_dwelling_markers(dwellings, "R");
            }
            """,
                                Output("featuregroup-markers2",
                                       "children",
                                       allow_duplicate=True),
                                Input(self.store_markers_R, 'data'),
                                prevent_initial_call=True)

        app.clientside_callback(
            ClientsideFunction(namespace='clientside',
                               function_name='track_state'),
            Output('url-output', 'search', allow_duplicate=True),
            [
                Input(self.L.store, 'data'),
                Input(self.R.store, 'data'),
                Input(self.mainview_tabs, 'active_tab'),
                Input(self.maintbl_preface_analysis_tabs, 'active_tab'),
                # Input(self.mainmap, 'zoom'),
                # Input(self.mainmap, 'center'),
            ],
            prevent_initial_call=True)
        # def track_state(fdL, fdR, tab, tab2):#, zoom, center):
        #     logger.debug(f'state changed, triggered by {ctx.triggered_id}: {fdL}, {fdR}, {tab}, {tab2}')#, {zoom}, {center}')
        #     state = {}
        #     for k,v in fdL.items(): state[k]=rejoin_sep(v)
        #     for k,v in fdR.items(): state[k+'2']=rejoin_sep(v)
        #     state['tab']=tab
        #     state['tab2']=tab2
        #     # state['lat']=center['lat']
        #     # state['lon']=center['lng']
        #     # state['zoom']=zoom
        #     state = {
        #         k:v
        #         for k,v in state.items() if v and DEFAULT_STATE.get(k)!=v
        #     }
        #     # logger.debug(f'state changed to: {state}')
        #     if not state: return ''
        #     ostr=f'?{urlencode(state)}'
        #     logger.debug(f'-> {ostr}')
        #     return ostr

        app.clientside_callback(ClientsideFunction(
            namespace='clientside', function_name='loadQueryParam'), [
                Output(self.L.store_incoming, 'data', allow_duplicate=True),
                Output(self.R.store_incoming, 'data', allow_duplicate=True),
                Output(self.mainview_tabs, 'active_tab', allow_duplicate=True),
                Output(self.maintbl_preface_analysis_tabs,
                       'active_tab',
                       allow_duplicate=True),
                Output(self.app_begun, 'data', allow_duplicate=True),
                Output('welcome-modal', 'is_open')
            ],
                                Input('url-input', 'search'),
                                State(self.app_begun, 'data'),
                                prevent_initial_call=True)

        ### TEST SUITE
        @app.callback(Output(self.test_suite, 'is_open', allow_duplicate=True),
                      Input(self.test_suite_btn, 'n_clicks'),
                      State(self.test_suite, 'is_open'),
                      prevent_initial_call=True)
        def test_suite_btn_onclick(n_clicks, is_open):
            return not is_open

        @app.callback(Output(self.L.member_panel.nation_card.store,
                             'data',
                             allow_duplicate=True),
                      Input('test_suite_btn1', 'n_clicks'),
                      prevent_initial_call=True)
        def test_suite_btn1_onclick(n_clicks):
            return {'member_nationalities': ['France']}

        @app.callback(Output(self.R.member_panel.nation_card.store,
                             'data',
                             allow_duplicate=True),
                      Input('test_suite_btn2', 'n_clicks'),
                      prevent_initial_call=True)
        def test_suite_btn2_onclick(n_clicks):
            return {'member_nationalities': ['United States']}

        @app.callback(Output(self.L.store, 'data', allow_duplicate=True),
                      Input('test_suite_btn5', 'n_clicks'),
                      prevent_initial_call=True)
        def test_suite_btn5_onclick(n_clicks):
            return {'member_gender': ['(Unknown)']}

        @app.callback(Output(self.L.member_panel.membership_year_card.graph,
                             'selectedData',
                             allow_duplicate=True),
                      Input('test_suite_btn6', 'n_clicks'),
                      prevent_initial_call=True)
        def test_suite_btn6_onclick(n_clicks):
            return {
                'points': [{
                    'curveNumber': 0,
                    'pointNumber': 8,
                    'pointIndex': 8,
                    'x': 1937,
                    'y': 21,
                    'label': 1937,
                    'value': 21
                }, {
                    'curveNumber': 0,
                    'pointNumber': 9,
                    'pointIndex': 9,
                    'x': 1938,
                    'y': 20,
                    'label': 1938,
                    'value': 20
                }, {
                    'curveNumber': 0,
                    'pointNumber': 10,
                    'pointIndex': 10,
                    'x': 1936,
                    'y': 19,
                    'label': 1936,
                    'value': 19
                }, {
                    'curveNumber': 0,
                    'pointNumber': 11,
                    'pointIndex': 11,
                    'x': 1933,
                    'y': 19,
                    'label': 1933,
                    'value': 19
                }, {
                    'curveNumber': 0,
                    'pointNumber': 12,
                    'pointIndex': 12,
                    'x': 1934,
                    'y': 19,
                    'label': 1934,
                    'value': 19
                }, {
                    'curveNumber': 0,
                    'pointNumber': 14,
                    'pointIndex': 14,
                    'x': 1939,
                    'y': 18,
                    'label': 1939,
                    'value': 18
                }, {
                    'curveNumber': 0,
                    'pointNumber': 16,
                    'pointIndex': 16,
                    'x': 1935,
                    'y': 16,
                    'label': 1935,
                    'value': 16
                }, {
                    'curveNumber': 0,
                    'pointNumber': 18,
                    'pointIndex': 18,
                    'x': 1932,
                    'y': 13,
                    'label': 1932,
                    'value': 13
                }],
                'range': {
                    'x': [1931.0454545454545, 1939.409090909091],
                    'y': [0, 37.89473684210526]
                }
            }
