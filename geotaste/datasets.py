from .imports import *


##################
##### Dataset #####
##################


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
        if self.fillna is not None: 
            df=df.fillna(self.fillna)
        for c in self.cols_sep: 
            df[c]=df[c].fillna('').apply(lambda x: [y.strip() for y in str(x).split(self.sep)])
        for c in self.cols_q:
            df[c]=pd.to_numeric(df[c], errors='coerce')
        if self.cols: 
            badcols = list(set(df.columns) - set(self.cols))
            df=df.drop(badcols, axis=1)
        if self.cols_rename: 
            df = df.rename(self.cols_rename, axis=1)
        return df

    def filter(self, filter_data={}, **other_filter_data):
        return intersect_filters(*[
            self.filter_series(key,vals)
            for key,vals in list(filter_data.items()) + list(other_filter_data.items())
        ])
    
    def filter_df(self, filter_data={}):
        # if not filter_data: filter_data=self.filter_data
        return filter_df(self.data, filter_data)

    def series(self, key) -> pd.Series:
        try:
            return self.data[key]
        except KeyError:
            try:
                return self.data_orig[key]
            except KeyError:
                pass
        return pd.Series()

    def filter_series(
            self, 
            key, 
            vals = [], 
            test_func = isin_or_hasone,
            matches = []
            ):
        
        return filter_series(
            series=self.series(key),
            vals=vals,
            test_func=test_func,
            series_name=key,
            matches = matches
        )
    
    

class LandmarksDataset(Dataset):
    path = PATHS.get('landmarks')
    cols_q = ['lat', 'lon']


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
    ]
    

    @cached_property
    def data(self):
        df=super().data
        df['member'] = df['uri'].apply(get_member_id)
        df['membership_years'] = [[int(y) for y in x if y] for x in df['membership_years']]
        
        # other
        df = df.set_index('member')
        return df



class DwellingsDataset(Dataset):
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
    cols_q = [
        'latitude',
        'longitude',
    ]
    # cols_id=['member','street_address','city','postal_code','start_date','end_date']
    cols_id = ['member', 'latitude', 'longitude','start_date','end_date']

    @cached_property
    def data(self):
        df=super().data
        df['member'] = df['member_uri'].apply(get_member_id)
        df['arrond_id']=df['arrrondissement'].apply(lambda x: 'X' if not x else str(int(x)))
        print(df['latitude'])
        print(df['longitude'])
        df['dist_from_SCO'] = [
            geodist(latlon, LATLON_SCO, unit='km')
            for latlon in zip(df.latitude, df.longitude)
        ]
        print(df.dist_from_SCO)
        df['desc'] = df.apply(get_dwelling_desc, axis=1)
        df['dwelling'] = [self.sep.join(str(x) for x in l) for l in df[self.cols_id].values]
        # logger.debug(df.dwelling)
        # logger.debug([len(df),'len df1'])
        # logger.debug(df.dwelling.value_counts())
        # df=df.drop_duplicates('dwelling')
        return df.set_index('dwelling')

    def get_member(self, member):
        return self.data[self.data['member'] == member]
    





def get_dwelling_desc(row):
    member_name = Members().data.loc[row.member]['name']
    o=f'{member_name} dwelt in {row.city}'
    if row.arrond_id and is_valid_arrond(row.arrond_id): 
        o+=f' in the {ordinal_str(int(row.arrond_id))}'
    if row.street_address: o+=f' at {row.street_address}'
    if row.start_date: o+=f' from {row.start_date}'
    if row.end_date and row.end_date!=row.start_date: o+=f' until {row.end_date}'
    return o







#########
# BOOKS











def get_book_id(uri):
    return uri.split('/books/',1)[1][:-1] if '/books/' in uri else ''

class BooksDataset(Dataset):
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

    cols_q = ['year', 'borrow_count', 'purchase_count']

    @cached_property
    def data(self):
        df=super().data
        df['book']=df.uri.apply(lambda x: x.split('/books/',1)[1][:-1] if '/books/' in x else '')
        return df.set_index('book')






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
        'Language',
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
    
    @cached_property
    def data(self):
        def reformat_nation(x):
            x=x.strip()
            if ' - ' in x:
                x=x.split(' - ',1)[-1]
            if x.endswith('-'): x=x[:-1]
            return [x.strip()]

        df=super().data
        df.columns = [c.lower().replace(' ','_') for c in df]
        df['creator']=df['sort_name']  # needs to be name for now  .apply(to_name_id)
        df['nationalities'] = df['nationality'].apply(reformat_nation)
        return df.set_index('creator')


def to_name_id(x):
    x=''.join(y for y in x if y.isalpha() or y==' ')
    return x.strip().replace(' ','-').lower()


class CreationsDataset(Dataset):
    cols_creators = [
        'author',
        'editor',
        'translator',
        'introduction',
        'illustrator',
        'photographer'
    ]


    @cached_property
    def data(self):
        books_df = Books().data
        creators_df = CreatorsDataset().data
        creators = set(creators_df.index)

        o=[]
        for book_id,row in books_df.iterrows():
            rowd=dict(row)
            rowd_nocr = {k:v for k,v in rowd.items() if k not in set(self.cols_creators)}
            cdone=0
            for col_creator in self.cols_creators:
                for creator in rowd[col_creator]:
                    if creator.strip():
                        odx={
                            'book':book_id,
                            'creator':creator,
                            'creator_role':col_creator,
                            **{f'creator_{k.lower()}':v for k,v in (creators_df.loc[creator] if creator in creators else {}).items()},
                            **{f'book_{k}':v for k,v in rowd_nocr.items()},
                        }
                        o.append(odx)
                        cdone+=1
            if not cdone:
                odx={
                    'book':book_id,
                    'creator':'?',
                    'creator_role':'author',
                    **{f'book_{k}':v for k,v in rowd_nocr.items()},
                }
                o.append(odx)

        return pd.DataFrame(o).fillna(self.fillna).set_index('book')






@cache
def Books(): return BooksDataset()










##########
# EVENTS







class EventsDataset(Dataset):
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

    @cached_property
    def data(self):
        df=super().data
        df['event']=[f'E{i+1:05}' for i in range(len(df))]
        df['start_year'] = pd.to_numeric([estr[:4] for estr in df['start_date'].apply(str)], errors='coerce')
        df['start_month'] = pd.to_numeric([
            x[5:7] if len(x)>=7 and x[:4].isdigit() and x[4]=='-' else None
            for x in df['start_date'].apply(str)
        ], errors='coerce')
        return df.set_index('event')



class MemberEventsDataset(EventsDataset):
    cols_events = [
        'event_type',
        'start_date',
        'end_date'
    ]
    
    @cached_property
    def data(self):
        l=[]
        for event,row in super().data.iterrows():
            for i,member_uri in enumerate(row['member_uris']):
                d={
                    'member':get_member_id(member_uri),
                    'book':get_book_id(row['item_uri']),
                    'event':event,
                    **dict(row)
                }
                l.append(d)
        df_events = pd.DataFrame(l)
        return df_events.merge(
            Members().data, 
            on='member', 
            how='outer',
            suffixes=('','_member')
        ).fillna('')

@cache
def MemberEvents(): return MemberEventsDataset()

@cache
def Events(): return EventsDataset()







class MemberEventDwellingsDataset(MemberEventsDataset):
    @cached_property
    def data(self):
        ld=[]
        df=super().data
        for i,row in tqdm(list(df.iterrows()), desc='Finding dwellings'):
            matches, reason = find_dwelling_ids(row)
            for match in matches:
                match_d=Dwellings().data.loc[match] if match else {}
                d={
                    'dwelling':match,
                    'dwelling_reason':reason,
                    'dwelling_numposs':len(matches),
                    **{f'dwelling_{k}':v for k,v in match_d.items()},
                    **dict(row),
                }
                ld.append(d)
        return pd.DataFrame(ld)
    



def is_valid_arrond(x):
    return bool(str(x).isdigit()) and bool(x!='99')

def filter_valid_arrond(df):
    return (df.index.str.isdigit()) & (df.index!='99')


def find_dwelling_ids(event_row, sep=DWELLING_ID_SEP, verbose=True, dispreferred = DISPREFERRED_ADDRESSES, cache=True):
    df = Dwellings().get_member(event_row.member)
    
    # if no dwelling at all?
    if not len(df): 
        return [''], '❓ No dwelling for member'
    
    # if only one?
    elif len(df)==1: 
        return list(df.index), '✅ Only one dwelling'
    
    
    # ok, if multiple:
    else:
        # try dispreferred caveats
        addresses = set(df.street_address)
        bad_address = list(addresses & set(DISPREFERRED_ADDRESSES.keys()))
        bad_address_str = ", ".join(bad_address)
        bad_address_reason = dispreferred[bad_address_str] if bad_address else ''
        df = df[~df.street_address.isin(dispreferred)]
        if len(df)==0: 
            return [''], f'❓ No dwelling after dispreferred filter ({bad_address_str} [{bad_address_reason}])'
        elif len(df)==1:
            return list(df.index), f'✅ One dwelling after dispreferred filter ({bad_address_str} [{bad_address_reason}])'
        else:
            # if start date?
            borrow_start = event_row.start_date
            borrow_end = event_row.end_date

            if borrow_start and borrow_end:
                if borrow_start:
                    # If we know when the borrow began, then exclude dwellings which end before that date
                    df = df[df.end_date.apply(lambda x: not (x and x[:len(borrow_start)]<borrow_start))]
                if borrow_end:
                    # If we know when the borrow ended, then exclude dwellings which begin after that date
                    df = df[df.start_date.apply(lambda x: not (x and x[:len(borrow_end)]>borrow_end))]
                
                # No longer ambiguous?
                if len(df)==0: return [''], '❓ No dwelling after time filter'
                elif len(df)==1: return list(df.index), '✅ One dwelling time filter'
                
                
            # Remove the non-Parisians?
            df = df[pd.to_numeric(df.dist_from_SCO,errors='coerce') < 50]  # less than 50km
            if len(df)==0: 
                return [''], f'❓ No dwelling after 50km filter'
            elif len(df)==1:
                return list(df.index), f'✅ One dwelling after 50km filter'
                
        return list(df.index), f'❌ {len(df)} dwellings after all filters'
        









class CombinedDataset(Dataset):
    path=PATHS.get('combined')
    fillna=''
    cols_creations = {
        'creator':'creator', 
        'creator_sort_name':'creator_name',
        'creator_role':'creator_role',
        'creator_birth_date':'creator_dob',
        'creator_death_date':'creator_dod',
        'creator_gender':'creator_gender',
        'creator_nationalities':'creator_nationalities',
    }
    cols_books = {
        'title':'book_title',
        'year':'book_year',
        'format':'book_format',
        'genre':'book_genre',

    }
    cols_members_events = {
        'member':'member',
        'title':'member_title',
        'sort_name':'member_name',
        'name':'member_nicename',
        'membership_years':'member_membership',
        'birth_year':'member_dob',
        'death_year':'member_dod',
        'gender':'member_gender',
        'nationalities':'member_nationalities',
        'event':'event',
        'book':'book',
        'dwelling':'dwelling',
        'dwelling_arrond_id':'arrond_id',
        'event_type':'event_type',
        'start_date':'event_start',
        'end_date':'event_end',
        'start_year':'event_year',
        'start_month':'event_month',
        'dwelling_desc':'dwelling_desc',
        'dwelling_numposs':'dwelling_numposs',
        'dwelling_reason':'dwelling_reason',
        'dwelling_start_date':'dwelling_start',
        'dwelling_end_date':'dwelling_end',
        'dwelling_street_address':'dwelling_address',
        'dwelling_city':'dwelling_city',
        'dwelling_latitude':'lat',
        'dwelling_longitude':'lon',
        'dwelling_dist_from_SCO':'dwelling_distSCO',
    }
    coltype_sort = ['member', 'event', 'book', 'dwelling', 'arrond', 'creator']
    cols_prefix = ['member', 'event', 'dwelling', 'lat', 'lon', 'arrond_id','book', 'creator']

    cols_q = ['member_dob', 'member_dod', 'creator_dob', 'creator_dod', 'book_year', 'lat', 'lon', 'event_year', 'event_month', 'dwelling_distSCO']
    cols_sep = ['member_nationalities', 'creator_nationalities', 'member_membership', 'book_genre']

    def gen(self, save=False):
        # events and members (full outer join)
        events_members = selectrename_df(
            MemberEventDwellings().data,
            self.cols_members_events
        )

        # creations and books (left join)
        creations = selectrename_df(CreationsDataset().data, self.cols_creations) #.query('@overlaps(creator_role, ["", "author"])')
        books = selectrename_df(BooksDataset().data, self.cols_books)
        creations_books = creations.join(books, how='outer')  # big to small, same index

        # all together (full outer join)
        odf = events_members.merge(
            creations_books, 
            on='book', 
            how='left'
        )
        for c in odf: 
            if c in set(self.cols_q):
                quant = True
            elif c not in set(self.cols_sep):
                quant = False
            else:
                quant = None
            odf[c] = qualquant_series(odf[c], quant=quant)

        odfx=odf.drop_duplicates('dwelling')
        bdf=odf[odf.book_title!='']
        tooltip_d = {
            row.dwelling:hover_tooltip(row, bdf) 
            for _,row in tqdm(
                odfx.iterrows(), 
                total=len(odfx), 
                desc='Pre-calculating tooltips'
            )
            if row.dwelling
        }
        odf['hover_tooltip'] = [tooltip_d.get(dw,'') for dw in odf.dwelling]
        if save: odf.to_pickle(self.path)
        return odf

    
    def load(self, force=False, save=True):
        # need to gen?
        if force or not os.path.exists(self.path):
            return self.gen(save=save)
        # otherwise load
        with Logwatch('reading pickled dataset'):
            return pd.read_pickle(self.path)
        
    @cached_property
    def data(self): 
        odf=self.load()
        with Logwatch('postprocessing CombinedDataset.data'):
            for c in self.cols_q: odf[c]=pd.to_numeric(odf[c], errors='coerce')
            # final filters?
            odf=odf.query('member!=""')  # ignore the 8 rows not assoc with members (books, in some cases empty events -- @TODO CHECK)
            return odf
    
    def filter_query_str(self, filter_data={}):
        return filter_query_str(
            filter_data, 
            multiline=False,
            plural_cols=self.cols_sep
        )





















def get_arrond_counts(df,key='arrond_id'):
    arrond_counts = {n:0 for n in sorted(get_all_arrond_ids(), key=lambda x: int(x) if x.isdigit() else np.inf)}
    for k,v in dict(df[key].value_counts()).items(): arrond_counts[k]=v    
    arrond_df = pd.DataFrame([arrond_counts]).T.reset_index()
    arrond_df.columns=[key, 'count']
    arrond_df = arrond_df.set_index(key).loc[filter_valid_arrond]
    arrond_df['perc']=arrond_df['count'] / sum(arrond_df['count']) * 100
    return arrond_df
    


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


@cache
def get_all_arrond_ids():
    ids_in_geojson = {
        d['id'] 
        for d in get_geojson_arrondissement()['features']
    }
    return {n for n in ids_in_geojson if n and n.isdigit() and n!='99'}# | {'X','?','99'} # outside of paris + unkown




@cache
def Members(): return MembersDataset()
@cache
def Dwellings(): return DwellingsDataset()
@cache
def MemberEventDwellings(): return MemberEventDwellingsDataset()
@cache
def Combined(): 
    logger.debug('Combined()')
    return CombinedDataset()


@cache
def Landmarks(): return LandmarksDataset()





#### other funcs

def hover_tooltip(row, bdf):
    UNKNOWN = '?'
    def v(x): return x if x else UNKNOWN
    
    if not row.member_membership:
        y1,y2 = UNKNOWN,UNKNOWN
    else:
        yl = sorted(list(row.member_membership))
        y1,y2 = yl[0],yl[-1]

    borrowdf_here = bdf[bdf.dwelling==row.dwelling].drop_duplicates('event')
    borrowdf_member = bdf[bdf.member==row.member].drop_duplicates('event')
    
    numborrow_member_total = len(borrowdf_member)
    numborrow_here = len(borrowdf_here)
    pronouns = ('they','their') if row.member_gender == 'Nonbinary' else (
        ('she','her') if row.member_gender=='Female' else (
            ('he','his') if row.member_gender == 'Male' else ('they','their')
        )
    )
    xn=50
    def wrap(x,xn=xn): return wraptxt(x, ensure_int(xn), '<br>') if x else x
    
    def bookdesc(r):
        o=f'* {r.creator}, <i>{r.book_title}</i> ({ensure_int(r.book_year)}), a {v(r.book_format.lower())}'
        if r.book_genre: o+=f' of {"and ".join(x.lower() for x in r.book_genre)}'
        o+=f' borrowed '
        if r.event_year and r.member_dob and is_numberish(r.member_dob) and is_numberish(r.event_year): 
            o+=f' when {int(float(r.event_year) - float(r.member_dob))}yo'
        if r.event_start:
            o+=f' {r.event_start}'
        if r.event_end:
            o+=f' and returned {r.event_end}'
        return wrap(o)
    
    borrowbooks = '<br><br>'.join(bookdesc(r) for i,r in borrowdf_here.fillna(UNKNOWN).iterrows())

    gdist = f'{round(float(row.dwelling_distSCO),1)}' if row.dwelling_distSCO else UNKNOWN
    nats=[x for x in row.member_nationalities if x.strip() and x!=UNKNOWN]
    nats=f', from {oxfordcomma(nats, repr=lambda x: x)}' if nats else ''
    gstr=f', {row.member_gender.lower()}'
    
    otitle = wrap(f'<b>{row.member_name}</b> ({v(ensure_int(row.member_dob))}-{v(ensure_int(row.member_dod))}){nats}{gstr}')
    obody = wrap(f'{row.member_title+" " if not row.member_nicename.startswith(row.member_title) else ""}{row.member_nicename} was a member of the library from {y1} to {y2}. {pronouns[0].title()} lived here, about {gdist}km from Shakespeare & Co, at {v(row.dwelling_address)} in {v(row.dwelling_city)}{", from "+row.dwelling_start if row.dwelling_start else ""}{" until "+row.dwelling_end if row.dwelling_end else ""}, where {pronouns[0]} borrowed {numborrow_here} of the {numborrow_member_total} books {pronouns[0]} borrowed during {pronouns[1]} membership. {"These books were:" if numborrow_here>1 else "This book was:"}')
    o = '<br><br>'.join([otitle, obody,borrowbooks])
    return o