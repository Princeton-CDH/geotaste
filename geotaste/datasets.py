from .imports import *


##################
##### PEOPLE #####
##################



class Dataset:
    id:str=''
    path:str = ''
    cols:list = []
    cols_sep:list = []
    cols_rename:dict = {}
    sep:str = ';'
    fillna:object = ''
    cols_q:list = []

    def __init__(self, path:str='', cols:list=[], **kwargs):
        if path: self.path=path
        if cols: self.cols=cols
        for k,v in kwargs.items(): setattr(self,k,v)

    @cached_property
    def _data(self):
        df=pd.read_csv(self.path, on_bad_lines='warn')
        if self.fillna is not None: 
            df=df.fillna(self.fillna)
        return df
        
    @cached_property
    def data(self):  
        df=self._data
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




class MembersDataset(Dataset):
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
        df['member'] = df['uri'].apply(
            lambda x: x.split('/members/',1)[1][:-1] if '/members/' in x else ''
        )
        df['membership_years'] = [[int(y) for y in x if y] for x in df['membership_years']]
        
        # other
        df = df.set_index('member')
        return df

    
    def data_table(
            self, 
            dff = None, 
            cols = ['name','title','gender','birth_year','death_year','nationalities']
            ):
        from dash import dash_table

        dff = self.data if dff is None else dff
        
        if cols: 
            dff=dff[cols]
        else:
            cols = dff.columns

        for col in set(cols) & set(self.cols_sep):
            dff[col] = dff[col].apply(lambda x: self.sep.join(str(y) for y in x))
        
        cols_l = [{'id':col, 'name':col} for col in cols] 
        # ddt, ddt_cols = dff.dash.to_dash_table()
        odt = dash_table.DataTable(
            data=dff.to_dict('records'),
            columns=cols_l,
            sort_action="native",
            sort_mode="multi",
            filter_action="native",
            page_action="native",
            page_size=5
        )
        return odt
    





class DwellingsDataset(Dataset):
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
    cols_rename:dict = {
        'start_date':'dwelling_start_date',
        'end_date':'dwelling_end_date',
    }
    cols_q = [
        'latitude',
        'longitude',
    ]



class MemberDwellingsDataset(Dataset):
    @cached_property
    def data(self):
        df_dwellings = DwellingsDataset().data
        df_members = MembersDataset().data
        return df_members.reset_index().merge(
            df_dwellings,
            left_on='uri',
            right_on='member_uri',
            how='inner'
        ).drop('member_uri',axis=1).set_index('member')


class BooksDataset(Dataset):
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

    @cached_property
    def data(self):
        df=super().data
        df['book']=df.uri.apply(lambda x: x.split('/books/',1)[1][:-1] if '/books/' in x else '')
        return df.set_index('book')






class CreatorsDataset(Dataset):
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
        df=super().data
        df['creator']=df['sort name']
        return df.set_index('creator')





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
        creators_df = Creators().data
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
                            **{f'creator_{k}':v for k,v in (creators_df.loc[creator] if creator in creators else {}).items()},
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

        return pd.DataFrame(o).fillna(self.fillna)










class EventsDataset(Dataset):
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

    


class MemberBookEventsDataset(Dataset):
    @cached_property
    def data(self):
        df_events=EventsDataset().data
        new_l = []
        for i,row in df_events.iterrows():
            book = row.item_uri.split('/books/',1)[1][:-1] if '/books/' in row.item_uri else ''
            for member_uri in row.member_uris:
                member = member_uri.split('/members/',1)[1][:-1] if '/members/' in member_uri else ''
                new_row = {
                    'member':member,
                    'book':book,
                    **{k:v for k,v in row.items() if k.split('_')[0] not in {'member','item'}}
                }
                new_l.append(new_row)
        new_df = pd.DataFrame(new_l)
        return new_df




def get_geojson_arrondissement(force=False):
    import os,json,requests
    
    url='https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson?lang=en&timezone=Europe%2FParis'
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













# @cache
def Members(): return MembersDataset()
# @cache
def MemberDwellings(): return MemberDwellingsDataset()
# @cache
def Books(): return BooksDataset()
# @cache
def Events(): return MemberBookEventsDataset()
