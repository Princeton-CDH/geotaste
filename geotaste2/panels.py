from .imports import *


class FilterPanel(FilterComponent):
    @cached_property
    def content(self,params=None):
        return dbc.Container([self.store] + super().content.children)

    def component_callbacks(self, app):
        super().component_callbacks(app)
        
        # intersect and listen
        @app.callback(
            Output(self.store, 'data',allow_duplicate=True),
            [
                Input(card.store, 'data')
                for card in self.subcomponents
            ],
            prevent_initial_call=True
        )
        def subcomponent_filters_updated(*filters_d):
            logger.debug('subcomponent filters updated')
            self.filter_data = self.intersect_filters(*filters_d)
            return self.filter_data
        


class FilterPlotPanel(FilterPanel):
    def component_callbacks(self, app):
        super().component_callbacks(app)
        @app.callback(
            [
                Output(card.graph,'figure',allow_duplicate=True)
                for card in self.graph_subcomponents
            ],
            Input(self.store, 'data'),
            prevent_initial_call=True
        )
        def redraw_graphs_from_new_data(panel_data):
            filtered_keys = set(panel_data.get('intension',{}).keys())
            return [
                (
                    dash.no_update 
                    if card.key in filtered_keys 
                    else card.plot(
                        filter_data = panel_data, 
                    )
                )
                for card in self.graph_subcomponents
            ]
        






class CombinedPanel(FilterPlotPanel):
    figure_factory = CombinedFigureFactory
    desc = 'Filters'
    records_name='members'

    @cached_property
    def member_name_card(self): 
        return MemberNameCard(name_prefix=self.name, **self._kwargs)
    
    @cached_property
    def member_dob_card(self): 
        return MemberDOBCard(name_prefix=self.name, **self._kwargs)
    
    @cached_property
    def membership_year_card(self): 
        return MembershipYearCard(name_prefix=self.name, **self._kwargs)
    
    @cached_property
    def member_gender_card(self): 
        return MemberGenderCard(name_prefix=self.name, **self._kwargs)
    
    @cached_property
    def member_nation_card(self): 
        return MemberNationalityCard(name_prefix=self.name, **self._kwargs)
    
    @cached_property
    def member_arrond_card(self): 
        return MemberArrondCard(name_prefix=self.name, **self._kwargs)

    @cached_property
    def subcomponents(self):
        return [
            # self.member_name_card,
            # self.membership_year_card,
            self.member_dob_card,
            # self.member_gender_card,
            # self.member_nation_card,
            # self.member_arrond_card,
        ]
    













class PanelComparison(FilterPanel):
    figure_factory = ComparisonFigureFactory
    # default_view = MemberMapView
    

    @cached_property
    def content(self,params=None):
        return dbc.Container([
            self.store,

            dbc.Row([
                
                # left col -- 6
                dbc.Col([
                    dbc.Row([
                        dbc.Col(
                            html.H2(['Left Group: ',self.L.store_desc]), 
                            width=6, 
                            className='storedescs-col storedescs-col-L left-color'
                        ),
                        
                        dbc.Col(
                            html.H2(['Right Group: ',self.R.store_desc]),
                            width=6, 
                            className='storedescs-col storedescs-col-R right-color'
                        ),
                    ], className='layout-toprow'), 

                    dbc.Row([
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
                    className='layout-mainrow'
                    )
                ], className='layout-leftcol', width=6),

                # right col
                dbc.Col(
                    dbc.Container([
                        dbc.Row(self.graphtabs, className='content-tabs-row'),
                        dbc.Row(self.graphtab, className='content-belowtabs-row'),
                    ]), 
                    className='layout-rightcol', width=6)
            ])
        ], className='panel-comparison-layout layout-belownavbar')
        
    @cached_property
    def subcomponents(self): return (self.L, self.R)

    @cached_property
    def L(self):
        return CombinedPanel(
            name=self.id('L-Panel'),
            L_or_R='L', 
            color=LEFT_COLOR, 
            desc='Left-hand Group Panel'
        )
    
    @cached_property
    def R(self):
        return CombinedPanel(
            name=self.id('R-Panel'),
            L_or_R='R', 
            color=RIGHT_COLOR, 
            desc='Right-hand Group Panel'
        )
    
    def intersect_filters(self, *filters_d):
        logger.debug(f'intersecting {len(filters_d)} filters')
        assert len(filters_d) == 2
        return (filters_d[0], filters_d[1])
    
    
    @cached_property
    def graphtabs(self):
        map_tabs = get_tabs([
            dict(label='Left vs. Right Groups', tab_id='map_LR'),
            dict(label='Left Group', tab_id='map_L'),
            dict(label='Right', tab_id='map_R'),
        ], tab_level=2, className='graphtabs-container')
        
        tbl_tabs = get_tabs(
            children=[
                dict(label='By arrondissement', tab_id='tbl_arrond'),
                dict(label='By member', tab_id='tbl_members'),                
            ], 
            tab_level=2, className='graphtabs-container'
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

    def determine_view(self, tab_ids_1=[], tab_ids_2=[], default=None):
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
        
        return default if default is not None else self.default_view



    def component_callbacks(self, app):
        super().component_callbacks(app)


        @app.callback(
            Output(self.graphtab, 'children'),
            [
                Input({"type": "tab_level_1", "index": ALL}, "active_tab"),
                Input({"type": "tab_level_2", "index": ALL}, "active_tab"),
                Input(self.store, 'data'),   # triggered by update! which means that self.filter_data and self.ff are updated as well
            ],
        )
        def repopulate_graphtab(tab_ids_1, tab_ids_2, filter_data):
            return html.P('!?!?')
            viewfunc = self.determine_view(tab_ids_1, tab_ids_2)
            return viewfunc(self)

