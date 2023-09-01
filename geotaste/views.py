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

def ArrondTableAndMapView(ff, Lstr='', Rstr=''):
    right_side=ArrondTableView(ff,Lstr=Lstr,Rstr=Rstr)
    left_side=MemberMapView(ff,choro=True,className='comparison_map_graph comparison_map_graph_choro')
    return dbc.Container(dbc.Row([dbc.Col(left_side), dbc.Col(right_side)]))





def MemberTableView(ff):
    return dbc.Container(
            [
                html.H4('Data'), 
                ff.table() if hasattr(ff,'table') else html.P('??')
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

def MemberMapView(ff, choro=None, className='comparison_map_graph', **kwargs):
    ofig = ff.plot_map(choro=choro, **kwargs)
    ofig.update_layout(autosize=True)
    ograph = dcc.Graph(
        figure=ofig, 
        className=className,
        config={'displayModeBar':False},
    )
    return dbc.Container(ograph, className='graphtab')