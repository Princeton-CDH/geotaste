from .imports import *


### Views


    

def ArrondTableView(ff, Lstr='', Rstr=''):
    # signif_df = ff.signif_arronds
    # if len(signif_df): 
    #     signif_df['odds_ratio'] = signif_df['odds_ratio'].replace(np.inf, np.nan)
    #     signif_df = signif_df[signif_df.odds_ratio.apply(is_numeric) & (~signif_df.odds_ratio.isna()) & (signif_df.odds_ratio!=0)]

    # # arronds_str = f', '.join(f'the {ordinal_str(int(x))}' for x in signif_df.index)
    # # arronds_str = f', '.join(ordinal_str(int(x)) for x in signif_df.index)
    # desc_top = f'''Comparing where library members in the left- and right-hand groups lived produces **{len(signif_df)}** statistically significant arrondissement.'''
    
    # signif_more_L=signif_df[signif_df.odds_ratio>1]
    # signif_more_R=signif_df[signif_df.odds_ratio<1]

    
    
    # desc_L=getdesc_arrond(signif_more_L, Lstr,side='left') if len(signif_more_L) else ''
    # desc_R=getdesc_arrond(signif_more_R, Rstr,side='right') if len(signif_more_R) else ''

    desc_L,desc_R = describe_arronds(ff.signif_arronds)

    return dbc.Container(
        [
            html.H4('Data by arrondissement'), 
            dcc.Markdown(desc_top),
            dbc.Row([
                dbc.Col(dcc.Markdown(desc_L, className='left-color')),
                dbc.Col(dcc.Markdown(desc_R, className='right-color'))
            ]),
            ff.table_arrond()
        ], 
        className='graphtab padded', 
    )






def MemberTableView(ff):
    return dbc.Container(
            [
                html.H4('Data by members'), 
                ff.table_members()
            ], 
            className='graphtab padded', 
        )


def DifferenceDegreeView(ff):
    return dbc.Container(
        [
            html.H4('Degree of difference compared'),
            html.P(
                dcc.Markdown(
                    ff.desc_table_diff()
                )
            ), 
            ff.table_diff()
        ], 
        className='graphtab padded', 
    )

def MemberMapView(ff):
    ofig = ff.plot()
    ofig.update_layout(autosize=True)
    ograph = dcc.Graph(
        figure=ofig, 
        className='comparison_map_graph',
        config={'displayModeBar':False},
    )
    return dbc.Container(ograph, className='graphtab')