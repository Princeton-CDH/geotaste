from ..imports import *
from .figs import *
from ..combined import CombinedPanel

class PanelComparison(FilterPanel):
    figure_factory = ComparisonFigureFactory

    

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
            name='CombinedPanel-L', 
            L_or_R='L', 
            color=LEFT_COLOR, 
            desc='Left-hand Group Panel'
        )
    
    @cached_property
    def R(self):
        return CombinedPanel(
            name='CombinedPanel-R', 
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
                    self.ff.table_members()
                ], 
                className='graphtab padded', 
            )
    
    @property
    def graphtab_tbl_arrond(self):
        signif_df = self.ff.signif_arronds
        if len(signif_df): 
            signif_df['odds_ratio'] = signif_df['odds_ratio'].replace(np.inf, np.nan)
            signif_df = signif_df[signif_df.odds_ratio.apply(is_numeric) & (~signif_df.odds_ratio.isna()) & (signif_df.odds_ratio!=0)]

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
            Output(self.graphtab, 'children'),
            [
                Input({"type": "tab_level_1", "index": ALL}, "active_tab"),
                Input({"type": "tab_level_2", "index": ALL}, "active_tab"),
                Input(self.L.store, 'data'), 
                Input(self.R.store, 'data'),
            ],
            # prevent_initial_call=True
        )
        def repopulate_graphtab(tab_ids_1, tab_ids_2, filter_data_L, filter_data_R):
            # print(f'Tab ID 1: {tab_ids_1}')
            # print(f'Tab ID 2: {tab_ids_2}')
            # self.log(f'Triggered: {ctx.triggered_id}')
            # if str(ctx.triggered_id).startswith('store-'):
            # self.ff = ComparisonFigureFactory(filter_data_L, filter_data_R)
            
            tab_ids_1_set=set(tab_ids_1)
            tab_ids_2_set=set(tab_ids_2)

            if 'tbl' in tab_ids_1_set:
                if 'tbl_members' in tab_ids_2_set:
                    return self.graphtab_tbl_members
                    
                elif 'tbl_arrond' in tab_ids_2_set:
                    return self.graphtab_tbl_arrond
                    
            elif 'analyze' in tab_ids_1_set:
                if 'tbl_diff' in tab_ids_2_set:
                    return self.graphtab_tbl_diff
            
            elif 'map' in tab_ids_1_set:
                return self.graphtab_map_members
            
            return html.Pre('Unknown tab?')

                

