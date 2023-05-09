from .imports import *



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
    df['has_wikipedia'] = df['wikipedia_url']==""
    # df['nation'] = df['nationalities'].apply(lambda x: x.split(';')[0])
    # df['is_expat'] = df['nationalities'].apply(lambda x: 'France' not in x)

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
def get_combined_df(lim=None, **kwargs):
    odf = get_event_dwellings_df(lim=lim).reset_index().merge(
        get_books_df().reset_index(),
        on='book_id',
        how='left',
        suffixes=('','_book')
    ).merge(
        get_members_df().reset_index(),
        on='member_id',
        how='left',
        suffixes=('','_member')
    ).set_index('event_dwelling_id')
    return odf






# book_choices = show_book_choices()

def get_combined_filtered_events_from_choices(data):
    return get_combined_filtered_events_for(**data)


def get_combined_filtered_events_for(
        books=None, 
        members=None,
        events=None, 
        authors=None,
        authors_key_author='author_sort_name',
        books_key_author='author',
        key_sep=';'
        ):
    
    if books is None: books=get_books_df()
    if members is None: members=get_members_df()
    if events is None: events=get_events_df()
    if authors is None: authors=get_authors_df()

    # make sure in member ids
    ok_members = set(members.index)

    ok_authors = set(authors[authors_key_author])
    def is_ok_author(x):  
        return bool({y.strip() for y in x.split(key_sep) if y.strip()} & ok_authors)
    books=books[books[books_key_author].apply(is_ok_author)]
    ok_books = set(books.index)

    # find synthesized data
    df = events[(events.member_id.isin(ok_members)) & (events.book_id.isin(ok_books))]
    
    # return located data (via members)
    return find_dwellings_for_member_events(df)