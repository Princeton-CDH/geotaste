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
    return figdf

def get_heatmap(book=None, event=None, year=None):
    figdf=get_mapdf(book=book,event=event,year=year)
    return draw_heatmap(figdf)
    
def draw_heatmap(figdf):
    latlon = figdf[['lat','lon']]
    centroid = latlon_SCO
    map = folium.Map(location=centroid, zoom_start=13, width='90%')
    hmap = folium.plugins.HeatMap(latlon)
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