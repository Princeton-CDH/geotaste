from .imports import *


## base DATASET class
class Dataset:
    id:str=''
    url:str = ''
    path:str = ''
    cols:list = []
    cols_sep:list = []
    cols_rename:dict = {}
    sep:str = ';'
    fillna:object = ''
    cols_q:list = []
    filter_data:dict = {}
    cols_pref:list = []

    def __init__(self, path:str='', cols:list=[], **kwargs):
        if path: self.path=path
        if cols: self.cols=cols
        for k,v in kwargs.items(): setattr(self,k,v)

    def read_df(self):
        assert self.path # assert path string exists
        if not os.path.exists(self.path):
            if self.url:
                # download and save
                df=pd.read_csv(self.url)
                # make dir if not exists
                if not os.path.exists(os.path.dirname(self.path)):
                    os.makedirs(os.path.dirname(self.path))
                # save csv
                df.to_csv(self.path, index=False)
                # return loaded df
                return df
            else:
                raise Exception('Neither URL nor path')
        # read from saved file
        df = pd.read_csv(self.path, on_bad_lines='warn')
        return df

    @cached_property
    def data(self):  
        df=self.read_df()
        return postproc_df(
            df,
            cols=self.cols_rename if self.cols_rename else self.cols,
            cols_sep=self.cols_sep,
            cols_q=self.cols_q,
            sep=self.sep,
            fillna=self.fillna
        )

    def filter_df(self, filter_data={}):
        return filter_df(self.data, filter_data)
    
    @cached_property
    def filter_desc(self):
        return filter_query_str(
            self.filter_data,
            human=True
        )
    
    

### LANDMARKS

class LandmarksDataset(Dataset):
    path = PATHS.get('landmarks')
    url = URLS.get('landmarks')
    cols_q = ['lat', 'lon']
    
    @cached_property
    def data(self):
        df=super().data
        df['arrond_id'] = [
            determine_arrond(lat,lon)
            for lat,lon in zip(df.lat, df.lon)
        ]

        df['tooltip'] = [
            f'''{row.landmark}\n{row.address}\n{'Paris '+row.arrond_id+'ᵉ' if row.arrond_id.isdigit() else ''}'''.strip().replace('\n','<br>')
            for i,row in df.iterrows()
        ]

        return df

@cache
def Landmarks(): return LandmarksDataset()



### MEMBERS

def get_member_id(uri):
    return uri.lower().split('/members/',1)[1][:-1] if '/members/' in uri else ''

class MembersDataset(Dataset):
    url:str = URLS.get('members')
    path:str = PATHS.get('members')
    sep:str = ';'
    cols:list = [
        'uri',
        'name',
        'sort_name',
        'title',
        'gender',
        'is_organization',
        'has_card',
        'birth_year',
        'death_year',
        'membership_years',
        'viaf_url',
        'wikipedia_url',
        'nationalities',
        # 'addresses',
        # 'postal_codes',
        # 'arrondissements',
        # 'coordinates',
        'notes',
        'updated'
    ]
    cols_sep:list = [
        'nationalities',
        'membership_years'
    ]
    cols_q = [
        'birth_year',
        'death_year',
        'membership_years'
    ]
    cols_pref = [
        'member',
        'member_nicename',
    ]
    

    @cached_property
    def data(self):
        df=super().data
        df['member'] = df['uri'].apply(get_member_id)
        df['nice_name'] = df['sort_name'].apply(to_name_nice)
        return postproc_df(df,cols_pref=self.cols_pref)

class MiniMembersDataset(MembersDataset):
    _cols_rename = {
        'member':'member',
        'nice_name':'member_name',
        'title':'member_title',
        'gender':'member_gender',
        'membership_years':'member_membership',
        'birth_year':'member_dob',
        'death_year':'member_dod',
        'gender':'member_gender',
        'nationalities':'member_nationalities',
    }
    cols_pref = [
        'member',
        'member_name',
    ]

    @cached_property
    def data(self):
        odf=postproc_df(super().data, self._cols_rename, cols_q=['member_dob', 'member_dod'])
        return odf
    
@cache
def Members(): return MiniMembersDataset()



### DWELLINGS   

class DwellingsDataset(Dataset):
    url:str = URLS.get('dwellings')
    url:str = URLS.get('dwellings')
    path:str = PATHS.get('dwellings')
    cols:list = [
        'member_uri',
        # 'person_id',
        # 'account_id',
        # 'address_id',
        # 'location_id',
        'start_date',
        'end_date',
        # 'start_date_precision',
        # 'end_date_precision',
        # 'care_of_person_id',
        'street_address',
        'city',
        'postal_code',
        'latitude',
        'longitude',
        # 'country_id',
        'arrrondissement'
    ]
    # cols_rename:dict = {
    #     'start_date':'dwelling_start_date',
    #     'end_date':'dwelling_end_date',
    # }
    # cols_rename:dict = {
    #     'start_date':'dwelling_start_date',
    #     'end_date':'dwelling_end_date',
    # }
    cols_q = [
        'latitude',
        'longitude',
    ]
    # cols_id=['member','street_address','city','postal_code','start_date','end_date']
    cols_id = ['member', 'latitude', 'longitude','start_date','end_date']

    cols_pref=[
        'dwelling',
        'member',
        'arrond_id',
        'street_address',
        'city',
        'postal_code',
        'latitude',
        'longitude',
        'start_date',
        'end_date'
    ]

    @cached_property
    def data(self):
        df=super().data
        df['member'] = df['member_uri'].apply(get_member_id)
        df['dwelling'] = [self.sep.join(str(x) for x in l) for l in df[self.cols_id].values]
        df['arrond_id']=df['arrrondissement'].apply(lambda x: '' if not x else str(int(x)))
        return postproc_df(df,cols_pref=self.cols_pref)
        
        
    
class MiniDwellingsDataset(DwellingsDataset):
    _cols_rename = dict(
        member='member',
        dwelling='dwelling',
        arrond_id='arrond_id',
        start_date='dwelling_start',
        end_date='dwelling_end',
        street_address='dwelling_address',
        city='dwelling_city',
        latitude='lat',
        longitude='lon',
    )

    @cached_property
    def data(self):
        return postproc_df(super().data, self._cols_rename)

@cache
def Dwellings(): return MiniDwellingsDataset()



### BOOKS

def get_book_id(uri):
    return uri.split('/books/',1)[1][:-1] if '/books/' in uri else ''

class BooksDataset(Dataset):
    url:str = URLS.get('books')
    url:str = URLS.get('books')
    path:str = PATHS.get('books')
    cols:list = [
        'uri',
        'title',
        'genre',
        'author',
        'editor',
        'translator',
        'introduction',
        'illustrator',
        'photographer',
        'year',
        'format',
        'uncertain',
        'ebook_url',
        'volumes_issues',
        'notes',
        'event_count',
        'borrow_count',
        'purchase_count',
        'circulation_years',
        'updated'
    ]

    cols_sep:list = [
        'author',
        'editor',
        'translator',
        'introduction',
        'illustrator',
        'photographer',
        'circulation_years',
        'genre'
    ]

    cols_q = ['year', 'borrow_count', 'purchase_count','circulation_years']
    cols_pref = ['book','title','author','year','genre']

    @cached_property
    def data(self):
        df=super().data
        df['book']=df.uri.apply(lambda x: x.split('/books/',1)[1][:-1] if '/books/' in x else '')
        return postproc_df(df, cols_pref=self.cols_pref)

class MiniBooksDataset(Dataset):
    ## ONLY AUTHORS
    _cols_rename={
        'book':'book',
        'author':'author',
        'author_nice_name':'author_name',
        'title':'book_title',
        'year':'book_year',
        'genre':'book_genre',
        'format':'book_format',
        'circulation_years':'book_circulated',
        'borrow_count':'book_numborrow',
        'author_birth_date':'author_dob',
        'author_death_date':'author_dod',
        'author_gender':'author_gender',
        'author_nationalities':'author_nationalities',
    }
    cols_sep = []
    cols_pref = ['book','author','author_name','book_title','book_year']

    @cached_property
    def data(self):
        dfbooks=BooksDataset().data.drop_duplicates('book')
        dfau=CreatorsDataset().data.drop_duplicates('creator').set_index('creator')
        ld=[]
        for i,row in dfbooks.iterrows():
            assert type(row.author) == list
            for author in row.author if row.author else ['']:
                d=dict(row)
                aid=d['author']=to_name_id(author)
                try:
                    for k,v in dict(dfau.loc[aid]).items():
                        d[f'author_{k}']=v
                except KeyError:
                    pass
                ld.append(d)
        odf=pd.DataFrame(ld)
        odf=postproc_df(odf, cols=self._cols_rename, cols_q=['author_dob','author_dod','book_year','book_circulated'], cols_pref=self.cols_pref)
        odf['author_nationalities']=odf['author_nationalities'].apply(
            lambda x: [] if x is np.nan else x
        )
        odf['author_gender']=odf['author_gender'].fillna('')
        odf['author_name']=odf['author_name'].fillna('')
        return odf

@cache
def Books(): return MiniBooksDataset()



### AUTHORS

class CreatorsDataset(Dataset):
    url:str = URLS.get('creators')
    path:str = PATHS.get('creators')
    cols:list = [
        # 'ID',
        # 'name',
        'sort name',
        # 'MEP id',
        # 'Account Id',
        # 'birth year',
        # 'death year',
        # 'gender',
        # 'title',
        # 'profession',
        # 'is organization',
        # 'Is Creator',
        # 'Has Account',
        # 'In Logbooks',
        # 'Has Card',
        # 'Subscription Dates',
        # 'verified',
        # 'updated at',
        # 'Admin Link',
        'VIAF id',
        # 'Key',
        'Gender',
        'Nationality',
        # 'Language',
        'Birth Date',
        'Death Date',
        # 'LoC Name',
        # 'LoC ID',
        # 'LoC Source: URL',
        # 'LofC URI: URL',
        # 'VIAF Source: URL',
        # 'BNE Name',
        # 'BNE URL',
        # 'BNF Name',
        # 'BNF URL',
        # 'DNB Name',
        # 'DNB URL',
        # 'ICCU Name',
        # 'ICCU URL',
        # 'ISNI Name',
        # 'ISNI URL',
        'Wikidata URL',
        # 'Wikipedia URL',
        # 'WorldCat Identity URL'
    ]
    cols_pref = ['creator', 'gender','nationality','birth_date','end_date']
    cols_sep = ['Nationality']
    
    @cached_property
    def data(self):
        df=super().data
        df.columns = [c.lower().replace(' ','_') for c in df]
        df['creator']=df['sort_name'].apply(to_name_id)
        df['nice_name']=df['sort_name'].apply(to_name_nice)
        odf=postproc_df(df, cols_pref=self.cols_pref)
        return odf.rename(columns={'nationality':'nationalities'})

def to_name_id(x):
    x=''.join(y for y in x if y.isalpha() or y==' ')
    return x.strip().replace(' ','-').lower()

def to_name_nice(x):
    if not ',' in x: return x
    a,b=x.split(',', 1)
    ln=a.strip()
    fn=b.split()[0].strip()
    return f'{fn} {ln}'



### EVENTS

class EventsDataset(Dataset):
    url:str = URLS.get('events')
    url:str = URLS.get('events')
    path:str = PATHS.get('events')
    cols:list = [
        'event_type',
        'start_date',
        'end_date',
        'member_uris',
        'member_names',
        'member_sort_names',
        'subscription_price_paid',
        'subscription_deposit',
        'subscription_duration',
        'subscription_duration_days',
        'subscription_volumes',
        'subscription_category',
        'subscription_purchase_date',
        'reimbursement_refund',
        'borrow_status',
        'borrow_duration_days',
        'purchase_price',
        'currency',
        'item_uri',
        'item_title',
        'item_volume',
        'item_authors',
        'item_year',
        'item_notes',
        'source_type',
        'source_citation',
        'source_manifest',
        'source_image'
    ]

    cols_sep:list = [
        'member_uris', 
        'member_names', 
        'member_sort_names'
    ]

    cols_pref = ['event']

    @cached_property
    def data(self):
        df=super().data
        df['event']=[f'E{i+1:05}' for i in range(len(df))]
        df['start_year'] = pd.to_numeric([estr[:4] for estr in df['start_date'].apply(str)], errors='coerce')
        df['start_month'] = pd.to_numeric([
            x[5:7] if len(x)>=7 and x[:4].isdigit() and x[4]=='-' else None
            for x in df['start_date'].apply(str)
        ], errors='coerce')
        return postproc_df(df,cols_pref=self.cols_pref)

class MiniEventsDataset(Dataset):
    only_borrows = True

    @cached_property
    def data(self):
        # disaggregate EventsDataset by member_uris and get books too
        ld=[]
        for i,row in EventsDataset().data.iterrows():
            if self.only_borrows and row.event_type!='Borrow': continue
            for i,member_uri in enumerate(row['member_uris']):
                d={
                    'event':row.event,
                    'event_type':row.event_type,
                    'member':get_member_id(member_uri),
                    'book':get_book_id(row.item_uri),
                    'event_start':row.start_date,
                    'event_end':row.end_date,
                    'event_year':str(ifnanintstr(row.start_year,'')),
                    'event_month':str(ifnanintstr(row.start_month,'')),
                }
                ld.append(d)
        dfevents = pd.DataFrame(ld)
        
        return dfevents

@cache
def Events(): return MiniEventsDataset()



### COMBINED

class CombinedDataset(Dataset):
    path=PATHS.get('combinedmini')
    url=URLS.get('combinedmini')
    _cols_sep = [
        'member_membership', 
        'member_nationalities', 
        'book_genre', 
        'book_circulated', 
        'author_nationalities'
    ]
    _cols_q = ['member_membership','member_dob','member_dod','lat','lon','book_year','author_dob','author_dod','event_year','event_month']
    _cols_sep_nonan=['member_membership']
    _cols_pref=['member','event','dwelling','arrond_id','book','author']

    def gen(self, save=True, progress=True, frac=None):
        dfmembers = Members().data
        dfbooks = Books().data
        dfevents = Events().data
        dfdwellings = Dwellings().data
        
        ## merge!
        bookevents = dfevents.merge(dfbooks, on='book', how='outer')
        memberdwellings = dfmembers.merge(dfdwellings, on='member', how='outer')
        odf = memberdwellings.merge(bookevents, on='member', how='outer').fillna('')
        
        # drop dups
        odf = odf.drop_duplicates(['member','event','book','dwelling'])

        ## clean up
        for c in self._cols_sep: 
            odf[c]=[[] if x is '' else x for x in odf[c]]
        for c in self._cols_q:
            odf[c]=[np.nan if x is '' else x for x in odf[c]]
        for c in self._cols_sep_nonan:
            odf[c]=[[y for y in x if not np.isnan(y) and y] for x in odf[c]]

        
        if frac is not None: odf=odf.sample(frac=frac)
        odf['hover_tooltip'] = odf.apply(hover_tooltip,axis=1)
        odf = prune_when_dwelling_matches(odf, progress=progress)
        odf = postproc_df(
            odf,
            cols_sep=self._cols_sep,
            cols_q=self._cols_q,
        )
        if save: odf.to_pickle(self.path)
        return odf

    
    @cached_property
    def data(self): 
        # need to gen?
        if not os.path.exists(self.path): 
            if self.url:
                with Logwatch(f'downloading combined dataset from: {self.url}'):
                    df=pd.read_pickle(self.url)
            else:
                with Logwatch('generating combined dataset'):
                    df=self.gen(save=False)

            # save
            ensure_dir(self.path)
            with Logwatch(f'saving combined dataset to: {self.path}'):
                df.to_pickle(self.path)

        else:
            df=pd.read_pickle(self.path)
        
        return postproc_df(df, cols_pref=self._cols_pref)
    
@cache
def Combined(): 
    logger.debug('Combined()')
    return CombinedDataset()



### OTHER

def is_valid_arrond(x):
    return bool(str(x).isdigit()) and bool(x!='99')

@cache
def get_geojson_arrondissement(force=False):
    import os,json,requests
    
    # download if nec
    url=URLS.get('geojson_arrond')
    fn=os.path.join(PATH_DATA,'arrondissements.geojson')
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

def hover_tooltip(row):
    return f"""
<a href="https://shakespeareandco.princeton.edu/members/{row.member}/">{row.member_name} ({ifnanintstr(row.member_dob)} – {ifnanintstr(row.member_dod)})
{row.dwelling_address}
{row.dwelling_city} {row.arrond_id}ᵉ

Member: {int(min(row.member_membership)) if row.member_membership else ''} – {int(max(row.member_membership)) if row.member_membership else ''}
""".strip().replace('\n','<br>')

def determine_arrond(lat, lon, default='NA'):
    # use shapely code
    import shapely.geometry as geo

    # get geojson of Paris arrondissement
    geojson = get_geojson_arrondissement()

    # encode incoming point
    point = geo.Point(lon, lat)
    
    # loop through features in geojson and find intersection
    for feature in geojson['features']: 
        polygon = geo.shape(feature['geometry'])
        if polygon.contains(point):
            return feature['properties']['arrond_id']
    
    # if none found, return default
    return default

def prune_when_dwelling_matches(df, progress=True):
    """Prunes the dataframe based on dwelling matches for events.
    
    Args:
        df (pandas.DataFrame): The input dataframe containing event and dwelling information.
    
    Returns:
        pandas.DataFrame: The pruned dataframe with only the rows that have valid dwelling matches.
    """
    
    df_nonevent, df_event=df[df.event==''],df[df.event!='']
    
    # anyone's ok if they're not an event
    numpossd = {ii:np.nan for ii in df.index}
    matchtyped={
        **{ii:'NA' for ii in df_nonevent.index},
        **{ii:'?' for ii in df_event.index}
    }
    matchfoundd={ii:None for ii in df.index}
    excludedd={ii:False for ii in df.index}


    def declare_impossible(xdf):
        # but declare them impossible to match to a dwelling
        for ii in xdf.index:
            matchtyped[ii]='Impossible'
            numpossd[ii]=0
            matchfoundd[ii]=False
            excludedd[ii]=True

    def declare_exact_match(xdf):
        for ii in xdf.index:
            matchtyped[ii]='Exact'
            matchfoundd[ii]=True
            numpossd[ii]=len(xdf)

    def declare_exact_miss(xdf):
        logger.trace(f'for event {e}, a certain match was found, with {len(xdf)} possibilities')
        for ii in xdf.index: 
            matchtyped[ii]='Exact (excl.)'
            excludedd[ii]=True
            matchfoundd[ii]=False

    def declare_ambiguous(xdf, caveats=[]):
        for ii in xdf.index: 
            probtype = 'Colens' if not len(xdf[xdf.dwelling_start!='']) else 'Raphael'
            mt=f'Ambiguous ({probtype})' if len(xdf)>1 else 'Singular'
            # if caveats: mt+=f' ({", ".join(caveats)})'
            matchtyped[ii]=mt
            matchfoundd[ii]=True
            numpossd[ii]=len(xdf)

    def find_exact_matches(xdf):
        erow=xdf.iloc[0]
        e1,e2=erow.event_start,erow.event_end
        match = xdf[[
            (is_fuzzy_date_seq(d1,e1,d2) or is_fuzzy_date_seq(d1,e2,d2))
            for (d1,d2) in zip(xdf.dwelling_start, xdf.dwelling_end)
        ]]
        logger.trace(f'found {len(match)} exact matches for {(e1, e2)} with options {list(zip(xdf.dwelling_start, xdf.dwelling_end))}')
        return match

    def declare_heuristic_miss(xdf, htype=''):
        for ii in xdf.index: 
            matchtyped[ii]=f'Heuristic (excl.{" by "+htype if htype else ""})'
            matchfoundd[ii]=False
            excludedd[ii]=True


    
    # for every event...
    for e,edf in tqdm(df_event.groupby('event'), total=df_event.event.nunique(), desc='Locating events',disable=not progress):
        logger.trace(f'event: {e}, with {len(edf)} dwelling possibilities')
        ## if there are no dwellings at all...
        nadf=edf[edf.dwelling=='']
        declare_impossible(nadf)

        edf=edf[edf.dwelling!=''].drop_duplicates('dwelling')
        if not len(edf):
            logger.trace(f'for event {e}, no dwelling possibilities because empty dwellings')
            continue
    
        # if certainty is possible, i.e. we have dwelling records with start and end dates...
        edf_certain = edf.query('dwelling_start!="" & dwelling_end!=""')
        if len(edf_certain):
            logger.trace(f'for event {e}, certainty is possible, with {len(edf_certain)} possibilities')
            # is there a match? a point where start or end of event is within range of dwelling start or end?
            edf_match = find_exact_matches(edf_certain)
            # if so, then add indices only for the match, not the other rows
            if len(edf_match):
                logger.trace(f'for event {e}, a certain match was found, with {len(edf_match)} possibilities')
                declare_exact_match(edf_match)
                declare_exact_miss(edf[~edf.index.isin(edf_match.index)])
                continue

        # try dispreferred caveats
        caveats=[]
        edf0 = edf
        edf = edf[~edf.dwelling_address.isin(DISPREFERRED_ADDRESSES)]
        if not len(edf):
            logger.trace(f'for event {e}, only a dispreferred address remained; allowing')
            edf=edf0
        elif len(edf)!=len(edf0):
            declare_heuristic_miss(edf0[~edf0.index.isin(edf.index)], htype='dispref')
            caveats.append('-dispref')

        # try distance caveat
        edf0 = edf
        edf = edf[[get_dist_from_SCO(lat,lon)<50 for lat,lon in zip(edf.lat, edf.lon)]]
        if not len(edf):
            logger.trace(f'for event {e}, only non-Parisian places remaining; allowing')
            edf=edf0
        elif len(edf)!=len(edf0):
            declare_heuristic_miss(edf0[~edf0.index.isin(edf.index)], htype='distance')
            caveats.append('-distance')

        # otherwise, declare ambiguous?
        logger.trace(f'for event {e}, still no matches found. using all {len(edf)} possible indices')
        declare_ambiguous(edf,caveats=caveats)
        
    # add to dataframe a few stats on the dwelling matches
    df['dwelling_matchfound'] = matchfoundd
    df['dwelling_matchtype'] = matchtyped
    df['dwelling_numposs'] = numpossd
    df['dwelling_excluded'] = excludedd
    df['dwelling_likelihood'] = 1/df['dwelling_numposs']

    # return only ok rows
    return df.loc[~df.dwelling_excluded]