from .imports import *



@cache
def get_gsheet_df(): return pd.read_csv(url_gsheet).fillna('')
@cache
def get_members_df(): return get_urlpath_df('members')
@cache
def get_books_df(): return get_urlpath_df('books')
@cache
def get_events_df(): return get_urlpath_df('events')


def get_urlpath_df(name, force=False):
    url=urls.get(name)
    path=paths.get(name)
    if force or not os.path.exists(path):
        df=pd.read_csv(url)
        df.to_csv(path,index=False)
    else:
        df=pd.read_csv(path)
    return df

def get_event_id(row):
    base=f'{row.member_id} {(row.event_type+"s").upper()} {row.book_id}'
    if row.item_volume:
        base+=f"[{row.item_volume.strip().replace(' ','-')})"
    if not row.start_date: 
        return base
    
    if row.end_date and row.start_date!=row.end_date:
        return f'{base} FROM {row.start_date} TO {row.end_date}'
    
    return f'{base} ON {row.start_date}'


@cache
def gen_combined_df():
    
    def get_arinsee(x):
        for y in str(x).split(';'):
            if y.strip().isdigit():
                return str(y.strip())

    ### TRY TO EXPAND rows by the semi-colon
    def getrowinfo(row, i):
        odx={}
        for k,v in dict(row).items():
            if ';' in str(v):
                vs = str(v).split(';')
                try:
                    v=vs[i]
                except IndexError:
                    print('!!',i,vs)
            odx[k]=v
        return odx
    
    df_events_expanded = pd.DataFrame(
        {**getrowinfo(row,mi), 'member_uri':muri}
        for i,row in get_events_df().iterrows()
        for mi,muri in enumerate(row.member_uris.split(';'))
    )

    # make sure no semicolons surviving
    for col in df_events_expanded.columns: 
        assert True not in set(df_events_expanded[col].apply(str).str.contains(';'))

    # join all datasets -- events link books and people
    df = df_events_expanded.merge(
        get_members_df(), 
        left_on='member_uris',
        right_on='uri',
        suffixes=('_event','_member')
    ).merge(
        get_books_df(),
        left_on='item_uri',
        right_on='uri',
        suffixes=('_event','_book')
    ).fillna('')

    
    # filters
    df['book_id']=df.item_uri.apply(lambda x: x.split('/books/',1)[1][:-1])
    df['member_id']=df.member_uris.apply(lambda x: x.split('/members/',1)[1][:-1])
    df['event_id'] = df.apply(get_event_id, axis=1)
    df=df.drop_duplicates('event_id')
    cols=['member_id','book_id','event_id']
    df=df.loc[
        df[cols].dropna().index  # rows
    ][
        cols + [c for c in df if c not in set(cols)]  # cols
    ]
    df['arrond_id']=df.arrondissements.apply(get_arinsee)

    return df.set_index('event_id')


def filter_combined_df(df):
    df2=pd.DataFrame(df)
    # filter for year?
    df = df[df.start_date.apply(str).str[:4].str.isdigit()]
    df['start_year'] = df['start_date'].fillna('').apply(lambda x: pd.to_numeric(str(x)[:4]))
    df['start_dec'] = df['start_year'] // 10 * 10

    # must have coords
    df = df[df.coordinates!='']

    # quick function
    
    ####
    # @TODO: we need to get first PARIS coordinates, not first coord period
    def get_first_coord(coords): return coords.split(';')[0]
    ####

    def get_lat(coord): return float(coord.split(',')[0]) if coord else np.nan
    def get_lon(coord): return float(coord.split(',')[1]) if coord else np.nan

    df['first_coordinates'] = df.coordinates.apply(get_first_coord)
    df['lat'] = df.first_coordinates.apply(get_lat)
    df['lon'] = df.first_coordinates.apply(get_lon)

    # valid coords
    df = df.loc[ df[['lat','lon']].dropna().index ]
    return df


@cache
def get_combined_df(**kwargs):
    return filter_combined_df(
        gen_combined_df(),
        **kwargs
    )

@cache
def get_borrow_df(**kwargs):
    return filter_combined_df(
        gen_combined_df(),
        **kwargs
    ).query('event_type=="Borrow"')



def get_choices():
    df=get_combined_df()
    counts = df.book_id.value_counts()
    books = sorted(list(set(df.book_id)), key=lambda x: -counts[x])
    book_choice = Dropdown(options=['*'] + books)
    event_choice = Dropdown(options=['*'] + sorted(list(set(df.event_type))))
    year_choice = Dropdown(options=['*'] + sorted(list(set(df.start_dec))))
    return (book_choice, event_choice, year_choice)


def get_mapdf(book=None, event='borrow', year=None):
    figdf = get_combined_df()
    if book and book!='*': figdf = figdf[figdf.book_id == book]
    if event and event!='*': figdf = figdf[figdf.event_type.str.lower() == event.lower()]
    if year and year!='*': figdf = figdf[figdf.start_dec == year]

    def get_arinsee(x):
        for y in str(x).split(';'):
            if y.strip().isdigit():
                return str(y.strip())
    figdf['arrond_id']=figdf.arrondissements.apply(get_arinsee)
    return figdf

def get_heatmap(book=None, event=None, year=None):
    figdf=get_mapdf(book=book,event=event,year=year)
    return draw_heatmap(figdf)
    
def draw_map(figdf,zoom=True,**kwargs):
    centroid = latlon_SCO
    opts=dict(location=centroid, zoom_start=13, width='90%')
    if not zoom: opts={**opts, **dict(zoom_control=False, scrollWheelZoom=False, dragging=False)}
    opts={**opts, **kwargs}
    map = folium.Map(**opts)
    return map

def draw_heatmap(figdf,zoom=True,**kwargs):
    map = draw_map(figdf,zoom=zoom,**kwargs)
    hmap = folium.plugins.HeatMap(figdf[['lat','lon']])
    hmap.add_to(map)
    return map
    

def i_heatmap():
    book_choice,event_choice,year_choice = get_choices()
    return interact(
        get_heatmap,
        book=book_choice, 
        event=event_choice, 
        year=year_choice
    )




def get_points(df): return df[['lat','lon']].values


def printm(x):
    from IPython.display import display, Markdown
    display(Markdown(x))



def compare_heatmaps(df1,df2,width=600,height=400,**kwargs):
    hmap1=draw_heatmap(df1,**kwargs)
    hmap2=draw_heatmap(df2,**kwargs)
    return compare_maps(hmap1,hmap2,width=width,height=height)

def compare_maps(map1,map2,width=600,height=600,return_str=False,**kwargs):
    iframe1 = get_iframe(map1,width=width,height=height,return_str=True,float='left',**kwargs)
    iframe2 = get_iframe(map2,width=width,height=height,return_str=True,**kwargs)
    ostr=iframe1 + iframe2
    return ostr if return_str else HTML(ostr)


# @cache
def get_geojson_arrondissement(force=False):
    url='https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson?lang=en&timezone=Europe%2FParis'
    fn=os.path.join(path_data,'arrondissements.geojson')
    if force or not os.path.exists(fn):
        data = requests.get(url)
        with open(fn,'wb') as of: 
            of.write(data.content)

    # load        
    with open(fn) as f:
        jsond=json.load(f)
        
    # anno
    for d in jsond['features']:
        d['id'] = str(d['properties']['c_ar'])
        d['properties']['arrond_id'] = d['id']
    
    return jsond




@cache
def get_all_arrond_ids():
    return {
        d['id'] 
        for d in get_geojson_arrondissement()['features']
    }



def get_arrond_counts(df,key='arrond_id'):
    arrond_counts = {n:0 for n in sorted(get_all_arrond_ids(), key=lambda x: int(x))}
    for k,v in dict(df[key].value_counts()).items(): arrond_counts[k]=v    
    arrond_df = pd.DataFrame([arrond_counts]).T.reset_index()
    arrond_df.columns=[key, 'count']
    arrond_df['perc']=arrond_df['count'] / sum(arrond_df['count']) * 100
    return arrond_df



def compare_heatmaps(df1,df2,width=600,height=400,**kwargs):
    hmap1=draw_heatmap(df1,**kwargs)
    hmap2=draw_heatmap(df2,**kwargs)
    return compare_maps(hmap1,hmap2,width=width,height=height)




def get_iframe(map, width=600, height=400, return_str=False, **attrs):
    src=map.get_root().render().replace('"', '&quot;')
    
    styled_default=dict(
        # display='inline-block',
        # width='49%',
        margin='0 auto',
        border='0',
    )
    
    styled = {**styled_default, **attrs}
    stylestr = '; '.join(f'{k}:{v}' for k,v in styled.items())
    ostr=f'<iframe srcdoc="{src}" width="{width}" height="{height}" style="{stylestr}"></iframe>'
    return ostr if return_str else HTML(ostr)


def compare_maps(map1,map2,width=600,height=600,return_str=False,**kwargs):
    iframe1 = get_iframe(map1,width=width,height=height,return_str=True,float='left',**kwargs)
    iframe2 = get_iframe(map2,width=width,height=height,return_str=True,float='right',**kwargs)
    ostr=iframe1 + iframe2
    return ostr if return_str else HTML(ostr)

def draw_choropleth(
        df, 
        heatmap=True, 
        key='arrond_id', 
        value='count', 
        count_df=None, 
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        **kwargs):
    hmap=draw_heatmap(df,**kwargs) if heatmap else draw_map(df,**kwargs)
    cdf=get_arrond_counts(df) if count_df is None else count_df
    cmap = folium.Choropleth(
        get_geojson_arrondissement(),
        data=cdf,
        columns=[key, value],
        key_on="feature.id",
        fill_color=fill_color,
        fill_opacity=fill_opacity,
        line_opacity=line_opacity,
    )
    
    cdfi=cdf.set_index(key)
    vkeys=set()
    for s in cmap.geojson.data['features']:
        for k,v in dict(cdfi.loc[s['id']]).items():
            vkeys.add(k)
            s['properties'][k] = round(float(v),2)
        
    # and finally adding a tooltip/hover to the choropleth's geojson
    folium.GeoJsonTooltip([key]+list(vkeys)).add_to(cmap.geojson)
    cmap.add_to(hmap)

    return hmap


def compare_choropleths(df1,df2,return_str=False,**kwargs):
    opts={**dict(zoom_start=12, zoom=False, heatmap=True, value='perc'), **kwargs}
    
    m1=draw_choropleth(df1, **opts)
    m2=draw_choropleth(df2, **opts)
    
    ## diff
    cdf1=get_arrond_counts(df1).set_index('arrond_id')
    cdf2=get_arrond_counts(df2).set_index('arrond_id')
    diff_df = (cdf1-cdf2)
    
    odf=pd.DataFrame()
    for c in cdf1: 
        odf[c+'1']=cdf1[c]
        odf[c+'2']=cdf2[c]
        odf[c+'1-2']=diff_df[c]
    odf=odf.sort_values('perc1-2')
    
    diff_opts = {**opts}
    diff_opts['heatmap']=False
    diff_opts['fill_color']='RdBu'
    m3=draw_choropleth(df1, count_df=diff_df.reset_index(), **diff_opts)
    
    htmlstr = compare_maps(m1,m2,return_str=True, height=600, width='50%')
    htmlstr+= f'<div style="clear:both";><center>{get_iframe(m3,return_str=True, height=600, width="50%")}</center></div>'
    display(HTML(htmlstr))
    display(odf)
    return htmlstr if return_str else HTML(htmlstr)
    

def get_col_choice(col, sort_by_count=False, description=''):
    DF=get_borrow_df()
    counts = DF[col].value_counts()
    books = sorted(list(set(DF[col])), key=lambda x: -counts[x] if sort_by_count else x)
    book_choice = Dropdown(
        options=['*'] + books, 
        description=col if not description else description,
    )
    book_choice.name=col
    return book_choice

def get_book_choice():
    return get_col_choice('item_title', description='Book')
def get_member_choice():
    return get_col_choice('member_sort_names', description='Member')
def get_author_choice():
    return get_col_choice('item_authors', description='Author')
def get_decade_choice():
    return get_col_choice('start_dec', description='Decade')
def get_gender_choice():
    return get_col_choice('gender', description='Member gender')





def get_df_from_choices(choices):
    df=get_borrow_df()
    for x in choices:
        if x.value and x.value!='*':
            df = df[df[x.name] == x.value]
    return df

def get_choice_desc(choices):
    l=[]
    for x in choices:
        if x.value and x.value!='*':
            l.append(x.name+': '+str(x.value))
    return '; '.join(l) if l else '(All borrow events)'

def get_choice_funcs():
    return [get_book_choice, get_author_choice, get_member_choice, get_decade_choice, get_gender_choice]

@cache
def get_choices_left():
    return [f() for f in get_choice_funcs()]
@cache
def get_choices_right():
    return [f() for f in get_choice_funcs()]

def draw_maps(e=None):
    df1=get_df_from_choices(get_choices_left())
    df2=get_df_from_choices(get_choices_right())
    desc1=get_choice_desc(get_choices_left())
    desc2=get_choice_desc(get_choices_right())
    with get_out():
        clear_output()
        display(HTML(f'''
            <div style="float:left; color:#1A5276;"><h2>{desc1}</h2></div>
            <div style="float:right; color:#7B241C"><h2>{desc2}</h2></div>
        '''))
        compare_choropleths(df1,df2)

def get_layout():
    button=Button(description='Draw maps')
    button.on_click(draw_maps)
    return HBox([
        VBox([Label('Left-hand map')]+get_choices_left()),
        VBox([Label('Right-hand map')]+get_choices_right()),
        button
    ])

def show_layout():
    display(get_layout())


@cache
def get_out(): return Output()

def show_comparator():
    show_layout()
    draw_maps()
    display(get_out())


def compare(): show_comparator()