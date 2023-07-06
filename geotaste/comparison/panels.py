from ..imports import *
from .figs import *

class PanelComparison(BaseComponent):
    def __init__(self, *x, **y):
        from ..combined import CombinedPanel

        super().__init__(*x,**y)
        self.L = CombinedPanel(name='comparison-panel-L', L_or_R='L', color=LEFT_COLOR)
        self.R = CombinedPanel(name='comparison-panel-R', L_or_R='R', color=RIGHT_COLOR)
        self.ff = ComparisonFigureFactory()
        self.store = dcc.Store(id=self.id('store'), data={})


    @cached_property
    def comparison_map_graph(self):
        return dcc.Graph(
            figure=go.Figure(), 
            className='comparison_map_graph'
        )
    
    @cached_property
    def comparison_map_graph_div(self):
        return html.Div(self.comparison_map_graph)
    
    @cached_property
    def comparison_map_table(self):
        return html.Div(
            html.Pre('Table placeholder'), 
            className='comparison_map_table'
        )
    
    @cached_property
    def dueling_maps_row(self, params=None):
        return dbc.Row([
            dbc.Col(self.L.map_graph, width=6),
            dbc.Col(self.R.map_graph, width=6),
        ], className='bimap-row')
    
    @cached_property
    def dueling_descs_row(self, params=None):
        return dbc.Row([
            dbc.Col(
                html.H2([
                    'Left Group: ', 
                    self.L.store_desc
                ]), 
                width=6, 
                className='storedescs-col storedescs-col-L left-color'
            ),
            dbc.Col(
                html.H2([
                    'Right Group: ', 
                    self.R.store_desc
                ]),
                width=6, 
                className='storedescs-col storedescs-col-R right-color'
            ),
        ], className='storedescs-row')
        
    def layout_top(self, params=None):
        return dbc.Container([
            self.store,
            self.dueling_descs_row,
            # self.toptabs       # -> this now moved up to navbar level in GeotasteLayout
        ])
    
    def layout_main(self, params=None):
        return dbc.Container([
            self.layout_dueling_panels(params)
        ])
    
    
    def layout_content(self, params=None):
        return dbc.Container([
            dbc.Row(self.graphtabs, className='content-tabs-row'),
            dbc.Row(self.graphtab, className='content-belowtabs-row'),
        ], className='layout-content-container')
    
    def layout_dueling_panels(self, params=None):
        return dbc.Row([
            dbc.Col(self.L.layout(params), width=6, className='panel_L panel'),
            dbc.Col(self.R.layout(params), width=6, className='panel_R panel'),
        ])
    

    @cached_property
    def toptabs(self):
        return dbc.Tabs([
            dbc.Tab(label='Members', tab_id='members'),
            dbc.Tab(label='Books', tab_id='books'),
            # dbc.Tab(label='Borrowing event', tab_id='events'),
        ], className='navtabs-container', active_tab='members')
    
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
            active_tab='tbl'
        )
        return dbc.Container(graphtabs, className='graphtabs-container-container')
    
    @cached_property
    def graphtab(self):
        return dbc.Container(
            children=[html.Pre('Loading...')],
            className='graphtab-div'
        )
    
    @property
    def graphtab_tbl_members(self):
        return dbc.Container(
                [
                    html.H4('Data by members'), 
                    html.P('Lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description lots of description '),
                    self.ff.table_members()
                ], 
                className='graphtab padded', 
            )
    
    @property
    def graphtab_tbl_arrond(self):
        signif_df = self.ff.signif_arronds
        if len(signif_df): 
            signif_df['odds_ratio'] = signif_df['odds_ratio'].replace(np.inf, np.nan)
            print(signif_df.odds_ratio.unique())
            signif_df = signif_df[signif_df.odds_ratio.apply(is_numeric) & (~signif_df.odds_ratio.isna()) & (signif_df.odds_ratio!=0)]

        print(signif_df)

        arronds_str = f', '.join(f'the {ordinal_str(int(x))}' for x in signif_df.index)
        arronds_str = f', '.join(ordinal_str(int(x)) for x in signif_df.index)
        desc_top = f'''Comparing where library members in the left- and right-hand groups lived produces **{len(signif_df)}** statistically significant arrondissement{": " if arronds_str else ""}.'''
        
        signif_more_L=signif_df[signif_df.odds_ratio>1]
        signif_more_R=signif_df[signif_df.odds_ratio<1]

        def getdesc(signif_df, filter_desc, side='left'):
            descs=['',f'The {side}-hand group (**{filter_desc}**) is...']
            for arrond_id,row in signif_df.sort_values('odds_ratio', ascending=side!='left').iterrows():
                ratio = row.odds_ratio
                cL,cR,pL,pR=row.count_L,row.count_R,row.perc_L,row.perc_R
                if side=='right':
                    if ratio == 0: continue
                    ratio=1/ratio
                    cL,cR=cR,cL
                    pL,pR=pR,pL
                cL2 = int(cL * pL)
                cR2 = int(cR * pR)
                astr=ordinal_str(int(arrond_id))
                # descs+=[f'* *{ratio:.1f}x* more likely to live in the **{astr}**', f'    * [{pL:.0f}% ({cL:.0f}) vs. {pR:.0f}% ({cR:.0f})\]']
                # descs+=[f'* ***{ratio:.1f}x*** more likely to live in the **{astr}** ({pL:.1f}% vs. {pR:.1f}%)']
                descs+=[f'* ***{ratio:.1f}x*** more likely to live in the **{astr}** ({pL:.1f}% = {cL:.0f}/{cL2:.0f} vs. {pR:.1f}% = {cR:.0f}/{cR2:.0f})']
            return '\n'.join(descs)
        
        desc_L=getdesc(signif_more_L, self.L.filter_desc,side='left') if len(signif_more_L) else ''
        desc_R=getdesc(signif_more_R, self.R.filter_desc,side='right') if len(signif_more_R) else ''
        return dbc.Container(
            [
                html.H4('Data by arrondissement'), 
                dcc.Markdown(desc_top),
                dbc.Row([
                    dbc.Col(dcc.Markdown(desc_L, className='left-color')),
                    dbc.Col(dcc.Markdown(desc_R, className='right-color'))
                ]),
                self.ff.table_arrond()
            ], 
            className='graphtab padded', 
        )
    
    @property
    def graphtab_tbl_diff(self):
        return dbc.Container(
                [
                    html.H4('Degree of difference compared'),
                    html.P(
                        dcc.Markdown(
                            self.ff.desc_table_diff()
                        )
                    ), 
                    self.ff.table_diff()
                ], 
                className='graphtab padded', 
            )
    
    @property
    def graphtab_map_members(self):
        ofig = self.ff.plot()
        ofig.update_layout(autosize=True)
        ograph = dcc.Graph(
            figure=ofig, 
            className='comparison_map_graph'
        )
        return dbc.Container(ograph, className='graphtab')




    def component_callbacks(self, app):
        super().component_callbacks(app)

        @app.callback(
            output=[
                (
                    Output(self.L.member_panel_row, 'style', allow_duplicate=True),
                    Output(self.R.member_panel_row, 'style', allow_duplicate=True),
                ),
                (
                    Output(self.L.book_panel_row, 'style', allow_duplicate=True),
                    Output(self.R.book_panel_row, 'style', allow_duplicate=True),
                )
            ],
            inputs=[Input(self.toptabs, 'active_tab')],
            prevent_initial_call=True
        )
        def switch_toptabs(tab_id, num_tabs=2):
            invis=tuple([STYLE_INVIS for n in range(num_tabs)])
            vis=tuple([STYLE_VIS for n in range(num_tabs)])
            return (invis,vis) if tab_id=='books' else (vis,invis)
        



        @app.callback(
            Output(self.graphtab, 'children', allow_duplicate=True),
            [
                Input({"type": "tab_level_1", "index": ALL}, "active_tab"),
                Input({"type": "tab_level_2", "index": ALL}, "active_tab"),
                Input(self.L.store, 'data'), 
                Input(self.R.store, 'data'),
            ]
        )
        def repopulate_graphtab(tab_ids_1, tab_ids_2, filter_data_L, filter_data_R):
            print(f'Tab ID 1: {tab_ids_1}')
            print(f'Tab ID 2: {tab_ids_2}')
            print(f'Triggered: {ctx.triggered_id}')
            if str(ctx.triggered_id).startswith('store-'):
                self.ff = ComparisonFigureFactory(filter_data_L, filter_data_R)
            
            tab_ids_1_set=set(tab_ids_1)
            tab_ids_2_set=set(tab_ids_2)

            if 'tbl' in tab_ids_1_set:
                if 'tbl_members' in tab_ids_2_set:
                    print('returning tbl_members')
                    return self.graphtab_tbl_members
                    
                elif 'tbl_arrond' in tab_ids_2_set:
                    print('returning tbl_arrond')
                    return self.graphtab_tbl_arrond
                    
            elif 'analyze' in tab_ids_1_set:
                if 'tbl_diff' in tab_ids_2_set:
                    print('returning tbl_diff')
                    return self.graphtab_tbl_diff
            
            elif 'map' in tab_ids_1_set:
                print('returning map')
                return self.graphtab_map_members
            
            return html.Pre('Unknown tab?')

                

