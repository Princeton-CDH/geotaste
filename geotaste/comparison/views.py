from ..imports import *


### Views

def ArrondTableView(self):
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






def MemberTableView(self):
    return dbc.Container(
            [
                html.H4('Data by members'), 
                self.ff.table_members()
            ], 
            className='graphtab padded', 
        )


def DifferenceDegreeView(self):
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

def MemberMapView(self):
    ofig = self.ff.plot()
    ofig.update_layout(autosize=True)
    ograph = dcc.Graph(
        figure=ofig, 
        className='comparison_map_graph'
    )
    return dbc.Container(ograph, className='graphtab')