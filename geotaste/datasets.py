from .imports import *


##################
##### Dataset #####
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
    prefcols:list = []

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
    
    def postproc_df(self, df=None):
        return postproc_df(
            df=df if df is not None else self.data,
            prefcols=self.prefcols,    
            cols_rename=self.cols_rename
        )

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
    
    @cached_property
    def filter_desc(self):
        return filter_query_str(
            self.filter_data,
            human=True
        )
    
    

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
        
        

    def get_member(self, member):
        return self.data[self.data['member'] == member]
    





def get_dwelling_desc(row):
    try:
        member_name = Members().data.loc[row.member]['name']
        o=f'{member_name} dwelt in {row.city}'
        if row.arrond_id and is_valid_arrond(row.arrond_id): 
            o+=f' in the {ordinal_str(int(row.arrond_id))}'
        if row.street_address: o+=f' at {row.street_address}'
        if row.start_date: o+=f' from {row.start_date}'
        if row.end_date and row.end_date!=row.start_date: o+=f' until {row.end_date}'
    except KeyError:
        o='???'
    return o







#########
# BOOKS











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






class CreatorsDataset(Dataset):
    url:str = URLS.get('creators')
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
def Books(): return MiniBooksDataset()










##########
# EVENTS







##########
# EVENTS







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


@cache
def Events(): return MiniEventsDataset()







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
                dfq=df
                if borrow_start:
                    # If we know when the borrow began, then exclude dwellings which end before that date
                    dfq = dfq[dfq.end_date.apply(lambda x: not (x and x[:len(borrow_start)]<borrow_start))]
                if borrow_end:
                    # If we know when the borrow ended, then exclude dwellings which begin after that date
                    dfq = dfq[dfq.start_date.apply(lambda x: not (x and x[:len(borrow_end)]>borrow_end))]
                
                # No longer ambiguous?
                if len(dfq)==0: return list(df.index), '❓ No dwelling after time filter'
                elif len(dfq)==1: return list(dfq.index), '✅ One dwelling time filter'
                
                
            # Remove the non-Parisians?
            dfq = df[pd.to_numeric(df.dist_from_SCO,errors='coerce') < 50]  # less than 50km
            if len(dfq)==0: 
                return list(df.index), f'❓ No dwelling after 50km filter'
            elif len(dfq)==1:
                return list(dfq.index), f'✅ One dwelling after 50km filter'
                
        return list(df.index), f'❌ {len(df)} dwellings after all filters'
        









class CombinedDataset(Dataset):
    path=PATHS.get('combined')
    fillna=''
    cols_creations = {
        # 'creator':'creator', 
        # 'creator_sort_name':'creator_name',
        # 'creator_role':'creator_role',
        # 'creator_birth_date':'creator_dob',
        # 'creator_death_date':'creator_dod',
        # 'creator_gender':'creator_gender',
        # 'creator_nationalities':'creator_nationalities',
        
        'creator':'author',
        'creator_sort_name':'author_name',
        'creator_role':'author_role',
        'creator_birth_date':'author_dob',
        'creator_death_date':'author_dod',
        'creator_gender':'author_gender',
        'creator_nationalities':'author_nationalities',
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
    coltype_sort = ['member', 'event', 'book', 'dwelling', 'arrond_id', 'creator']
    cols_prefix = ['member', 'event', 'dwelling', 'lat', 'lon', 'arrond_id','book', 'creator']

    cols_q = ['member_dob', 'member_dod', 'author_dob', 'author_dod', 'book_year', 'lat', 'lon', 'event_year', 'event_month', 'dwelling_distSCO']
    cols_sep = ['member_nationalities', 'author_nationalities', 'member_membership', 'book_genre']

    def gen(self, save=False):
        # events and members (full outer join)
        events_members = selectrename_df(
            MemberEventDwellings().data,
            self.cols_members_events
        )

        # only borrows!
        events_members = events_members[
            events_members.event_type.isin(
                {'','Borrow'}
            )
        ]

        # creations and books (left join)
        crdf=CreationsDataset().data
        crdf=crdf[crdf.creator_role.isin({'','author'})] # only authors!
        creations = selectrename_df(crdf, self.cols_creations)

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

        odf['member_nicename'] = odf['member_name'].apply(to_name_nice)
        odf['hover_tooltip'] = [tooltip_d.get(dw,'') for dw in odf.dwelling]
        if save: odf.to_pickle(self.path)
        return odf

    
    def load(self, force=False, save=True):
        # need to gen?
        if force or not os.path.exists(self.path):
            return self.gen(save=save)
        return pd.read_pickle(self.path)
        
    @cached_property
    def data(self): 
        odf=self.load()
        with Logwatch('postprocessing CombinedDataset.data'):
            for c in self.cols_q: odf[c]=pd.to_numeric(odf[c], errors='coerce')
            # final filters?
            odf=odf.query('member!=""')  # ignore the 8 rows not assoc with members (books, in some cases empty events -- @TODO CHECK)
            # odf=odf[odf.event_type.isin({'','Borrow'})]
            # odf=odf[odf.creator_role.isin({'','author'})]
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
def get_all_arrond_ids():
    ids_in_geojson = {
        d['id'] 
        for d in get_geojson_arrondissement()['features']
    }
    return {n for n in ids_in_geojson if n and n.isdigit() and n!='99'}# | {'X','?','99'} # outside of paris + unkown




@cache
def Members(): return MiniMembersDataset()
@cache
def Dwellings(): return MiniDwellingsDataset()
@cache
def Combined(): 
    logger.debug('Combined()')
    return MiniCombinedDataset()


@cache
def Landmarks(): return LandmarksDataset()





#### other funcs

def hover_tooltip(row):
    return f"""
<a href="https://shakespeareandco.princeton.edu/members/{row.member}/">{row.member_name} ({ifnanintstr(row.member_dob)} – {ifnanintstr(row.member_dod)})
{row.dwelling_address}
{row.dwelling_city} {row.arrond_id}ᵉ

Member: {int(min(row.member_membership)) if row.member_membership else ''} – {int(max(row.member_membership)) if row.member_membership else ''}
""".strip().replace('\n','<br>')



def hover_tooltip_maximalist(row, bdf):
    UNKNOWN = ''
    def v(x): return x if x else UNKNOWN
    
    if not row.member_membership:
        y1,y2 = UNKNOWN,UNKNOWN
    else:
        yl = sorted(list(row.member_membership))
        y1,y2 = yl[0],yl[-1]

    borrowdf_here = bdf[bdf.dwelling==row.dwelling].drop_duplicates('book')
    borrowdf_member = bdf[bdf.member==row.member].drop_duplicates('book')
    
    numborrow_member_total = borrowdf_member.book.nunique()
    numborrow_here = borrowdf_here.book.nunique()
    pronouns = ('they','their') if row.member_gender == 'Nonbinary' else (
        ('she','her') if row.member_gender=='Female' else (
            ('he','his') if row.member_gender == 'Male' else ('they','their')
        )
    )
    xn=50
    def wrap(x,xn=xn): return wraphtml(x, xn)
    
    def bookdesc(r):
        o=f'* {r.author}, <i>{r.book_title}</i> ({ensure_int(r.book_year)}), a {v(r.book_format.lower())}'
        if r.book_genre: o+=f' of {"and ".join(x.lower() for x in r.book_genre)}'
        o+=f' borrowed '
        if r.event_year and r.member_dob and is_numberish(r.member_dob) and is_numberish(r.event_year): 
            o+=f' when {int(float(r.event_year) - float(r.member_dob))}yo'
        if r.event_start:
            o+=f' {r.event_start}'
        if r.event_end:
            o+=f' and returned {r.event_end}'
        return wrap(o)
    
    # borrowbooks = '<br><br>'.join(bookdesc(r) for i,r in borrowdf_here.fillna(UNKNOWN).iterrows())
    gdist = f'{round(float(row.dwelling_distSCO),1)}' if row.dwelling_distSCO else UNKNOWN
    nats=[x for x in row.member_nationalities if x.strip() and x!=UNKNOWN]
    nats=f', from {oxfordcomma(nats, repr=lambda x: x)}, ' if nats else ''
    # gstr=f', {row.member_gender.lower()}'
    dob=ifnanintstr(row.member_dob,'')
    dod=ifnanintstr(row.member_dod,'')
    birthdeath=f'{dob} – {dod}'
    arrond=f'{row.arrond_id}ᵉ' if row.arrond_id else ''
    
    # return wrap(f'''<b>{row.member_nicename}</b>  – {v(ifnanintstr(row.member_dod,'?'))}){nats} was a member of the library from {y1} to {y2}. {pronouns[0].title()} lived here, about {gdist}km from Shakespeare & Co, at {v(row.dwelling_address)} in {v(row.dwelling_city)}{", from "+row.dwelling_start if row.dwelling_start else ""}{" until "+row.dwelling_end if row.dwelling_end else ""}, where {pronouns[0]} borrowed {numborrow_here} of the {numborrow_member_total} books {pronouns[0]} borrowed during {pronouns[1]} membership.')''')

    ostr = f"""
<a href="https://shakespeareandco.princeton.edu/members/{row.member}/">{row.member_nicename} ({birthdeath})
{row.dwelling_address}
{row.dwelling_city} {arrond}

Member: {y1} – {y2}
""".strip().replace('\n','<br>')
    return ostr







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









#####




































































































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

    @cached_property
    def data(self):
        odf=postproc_df(super().data, self._cols_rename)
        for c in ['member_dob','member_dod']:
            odf[c]=odf[c].apply(lambda x: int(x) if x else x)
        return odf
    










class MiniBooksDataset(BooksDataset):
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

    @cached_property
    def data(self):
        df=super().data
        dfau=CreatorsDataset().data.set_index('creator')
        ld=[]
        for i,row in df.iterrows():
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
        odf=postproc_df(odf, cols=self._cols_rename, cols_q=['author_dob','book_year'])
        odf['author_nationalities']=odf['author_nationalities'].apply(
            lambda x: [] if x is np.nan else x
        )
        odf['author_gender']=odf['author_gender'].fillna('')
        odf['author_name']=odf['author_name'].fillna('')
        return odf










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










class MiniCombinedDataset(Dataset):
    path=PATHS.get('combinedmini')
    url=URLS.get('combinedmini')
    _cols_sep = [
        'member_membership', 
        'member_nationalities', 
        'book_genre', 
        'book_circulated', 
        'author_nationalities'
    ]
    _cols_q = ['member_dob','member_dod','lat','lon','book_year','author_dob','author_dod']
    _cols_sep_nonan=['member_membership']
    _cols_pref=['member','event','dwelling','arrond_id','book','author']

    def gen(self, save=True):
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

        
        
        odf['hover_tooltip'] = odf.apply(hover_tooltip,axis=1)
        odf = prune_when_dwelling_matches(odf)
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
    

    
