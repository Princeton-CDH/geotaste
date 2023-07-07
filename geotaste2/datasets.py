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
            df[c]=df[c].fillna('').apply(lambda x: str(x).split(self.sep))
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
        if not filter_data: filter_data=self.filter_data
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
    
    











### datasets

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
    cols_id=['member','street_address','city','postal_code','start_date','end_date']

    @cached_property
    def data(self):
        df=super().data
        df['member'] = df['member_uri'].apply(get_member_id)
        df['arrond_id']=df['arrrondissement'].apply(lambda x: 'X' if not x else str(int(x)))
        df['dist_from_SCO'] = [
            round(geodist(latlon, LATLON_SCO, unit='km'), 3) 
            for latlon in zip(df.latitude, df.longitude)
        ]
        df['desc'] = df.apply(get_dwelling_desc, axis=1)
        df['dwelling'] = [self.sep.join(l) for l in df[self.cols_id].values]
        df=df.drop_duplicates('dwelling')
        return df.fillna('').set_index('dwelling')

    def get_member(self, member):
        return self.data[self.data['member'] == member]
    


@cache
def Members(): return MembersDataset()
@cache
def MemberDwellings(): return MemberDwellingsDataset()
@cache
def Dwellings(): return DwellingsDataset()




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
        'circulation_years'
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
                    'member_name':row['member_names'][i],
                    'member_sort_name':row['member_sort_names'][i],
                    **dict(row)
                }
                l.append(d)
        return pd.DataFrame(l)

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
        'format':'book_format'
    }
    cols_members = {
        'sort_name':'member_name',
        'membership_years':'member_membership',
        'birth_year':'member_dob',
        'death_year':'member_dod',
        'gender':'member_gender',
        'nationalities':'member_nationalities'
    }
    cols_events = {
        'member':'member',
        'event':'event',
        'book':'book',
        'dwelling':'dwelling',
        'event_type':'event_type',
        'start_date':'event_start',
        'end_date':'event_end',
        'dwelling_numposs':'dwelling_numposs',
        'dwelling_reason':'dwelling_reason',
        'dwelling_start_date':'dwelling_start',
        'dwelling_end_date':'dwelling_end',
        'dwelling_street_address':'dwelling_address',
        'dwelling_latitude':'dwelling_lat',
        'dwelling_longitude':'dwelling_lon',
        'dwelling_arrond_id':'dwelling_arrond',
        'dwelling_dist_from_SCO':'dwelling_distSCO'
    }
    coltype_sort = ['member', 'event', 'book', 'dwelling', 'creator']
    
    def gen(self, save=False):
        # events and members (full outer join)
        events = selectrename_df(MemberEventDwellingsDataset().data, self.cols_events)
        members = selectrename_df(MembersDataset().data, self.cols_members)
        events_members = events.merge(members,on='member',how='outer').fillna(self.fillna)

        # creations and books (left join)
        creations = selectrename_df(CreationsDataset().data, self.cols_creations)
        books = selectrename_df(BooksDataset().data, self.cols_books)
        creations_books = creations.join(books)  # big to small, same index

        # all together (full outer join)
        odf = events_members.merge(creations_books, on='book', how='outer').fillna(self.fillna)

        colsort = sorted(
            odf.columns, 
            key=lambda c: self.coltype_sort.index(c.split('_')[0])
        )
        odf = odf[list(colsort)].set_index(self.coltype_sort).sort_index()
        if save: odf.to_pickle(self.path)
        return odf

    
    def load(self, force=False, save=True):
        # need to gen?
        if force or not os.path.exists(self.path):
            return self.gen(save=save)
        # otherwise load
        return pd.read_pickle(self.path)
        
    @cached_property
    def data(self): 
        odf=self.load()

        # final filters?
        odf=odf.query('member!=""')  # ignore the 8 rows not assoc with members (books, in some cases empty events -- @TODO CHECK)
        return odf
    


















