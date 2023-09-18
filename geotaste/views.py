from .imports import *


### Views

def ArrondTableView(ff, Lstr='Filter 1', Rstr='Filter 2'):
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

    

def AnalysisTableView(ff, **kwargs):
    with Logwatch('returning view'):
        odf = ff.compare(**kwargs)
        fig = ff.plot_oddsratio_map(odf)
        # logger.debug(fig)
        odf['colpref'] = odf.col.apply(lambda x: x.split('_')[0])

        out = []
        ins = list(sorted(odf.groupby('colpref')))
        ins += [('all data',odf)]
        for colpref, colpref_df in sorted(ins):
            desc_L,desc_R = describe_comparison(colpref_df, lim=10)
            out_col = [
                # dbc.Row(html.H4(f'Most distinctive {colpref} features of Filter 1 vs. Filter 2')),
                
                dbc.Row([
                    dbc.Col([
                        html.H5([f'10 most distinctive {"features" if colpref=="all data" else colpref+"s"} for Filter 1 (', ff.L.filter_desc,')']),
                        dcc.Markdown('\n'.join(desc_L))
                    ], className='left-color'),

                    dbc.Col([
                        html.H5([f'10 most distinctive {"features" if colpref=="all data" else colpref+"s"} for Filter 2 (', ff.R.filter_desc,')']),
                        dcc.Markdown('\n'.join(desc_R))
                    ], className='right-color'),
                ])
            ]

            out_col.append(dbc.Row(get_dash_table(colpref_df)))

            out_tab = dbc.Tab(dbc.Container(out_col), label=colpref.title())

            out.append(out_tab)
        
        return dbc.Container([
            dbc.Row(html.H4(f'Distinctive arrondissement map')),
            dbc.Row(dcc.Graph(figure=fig, id='mini_arrond_analysis_map')),
            dbc.Row(html.H4(f'Distinctive feature data', className='distinctive-feature-h4')),
            dbc.Row(dbc.Tabs(out))
        ])

def ArrondTableAndMapView(ff, Lstr='', Rstr=''):
    right_side=ArrondTableView(ff,Lstr=Lstr,Rstr=Rstr)
    left_side=MapView(ff,choro=True,className='comparison_map_graph comparison_map_graph_choro')
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

def MapView(ff, choro=None, className='comparison_map_graph', **kwargs):
    ofig = ff.plot_map(choro=choro, **kwargs)
    ofig.update_layout(autosize=True)
    ograph = dcc.Graph(
        figure=ofig, 
        className=className,
        config={'displayModeBar':False},
    )
    return dbc.Container(ograph, className='graphtab', id='map_view')


def TableView(ff, title='Data',desc=''):
    if type(ff) is ComparisonFigureFactory:
        return AnalysisTableView(ff)
    
    # otherwise
    return dbc.Container(
        [
            html.H4(title), 
            html.P(desc),
            ff.table()
        ], 
        className='table_view_container'
    )


def get_ff_for_num_filters(fdL={}, fdR={}, **kwargs):
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

def get_mainmap_figdata(fdL={}, fdR={}):
    if fdL or fdR:
        odata=[]
        if fdL: odata.extend(CombinedFigureFactory(fdL).plot_map(color=LEFT_COLOR).data)
        if fdR: odata.extend(CombinedFigureFactory(fdR).plot_map(color=RIGHT_COLOR).data)
    else:
        odata = LandmarksFigureFactory().plot_map().data
    return odata


@cache_obj.memoize()
def get_cached_fig_or_table(args_id):
    fdL,fdR,active_tab,analysis_tab=unserialize(args_id)
    ff=get_ff_for_num_filters(fdL,fdR)
    logger.debug([args_id,ff])
    if active_tab=='map':
        out=ff.plot_map()
    else:
        pcols=[c for c in PREDICT_COLS if c.startswith(analysis_tab)] if analysis_tab else PREDICT_COLS
        out=ff.table(cols=pcols)
    return to_json_gz_str(out)

def to_json_gz_str(out):
    ojson=pio.to_json(out)
    ojsongz=b64encode(zlib.compress(ojson.encode()))
    ojsongzstr=ojsongz.decode('utf-8')
    return ojsongzstr

def from_json_gz_str(ojsongzstr):
    ojsongz=b64decode(ojsongzstr.encode())
    ojson=zlib.decompress(ojsongz)
    ojsonstr=ojson.decode('utf-8')
    obj=pio.from_json(ojsonstr)
    return obj


# @cache
# def get_server_cached_view(args_id):
#     fdL,fdR,active_tab=unserialize(args_id)
#     ff = get_ff_for_num_filters(fdL,fdR)
#     if active_tab=='map':
#         return MapView(ff)
#     else:
#         return TableView(ff)
    
