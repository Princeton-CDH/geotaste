from ..imports import *
from .figs import *
from .views import *
from ..combined import CombinedPanel

class PanelComparison(FilterPanel):
    figure_factory = ComparisonFigureFactory
    default_view = MemberMapView
    

    def layout(self, params=None):
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
            name=self.id('L'), 
            L_or_R='L', 
            color=LEFT_COLOR, 
            desc='Left-hand Group Panel'
        )
    
    @cached_property
    def R(self):
        return CombinedPanel(
            name=self.id('R'),
            L_or_R='R', 
            color=RIGHT_COLOR, 
            desc='Right-hand Group Panel'
        )
    
    def intersect_filters(self, *filters_d):
        self.log(f'intersecting {len(filters_d)} filters')
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
            className='graphtab-div'
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
            viewfunc = self.determine_view(tab_ids_1, tab_ids_2)
            return viewfunc(self)

