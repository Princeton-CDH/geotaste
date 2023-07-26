from .imports import *


### Views


    

def ArrondTableView(ff, Lstr='', Rstr=''):
    desc_L,desc_R,desc_top = describe_arronds(ff.signif_arronds)
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