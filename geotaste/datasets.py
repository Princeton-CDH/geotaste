from .imports import *


##################
##### PEOPLE #####
##################



class Dataset:
    id:str=''
    path:str = ''
    cols:list = []
    cols_sep:list = []
    sep:str = ';'
    fillna = ''

    def __init__(self, path:str='', cols:list=[]):
        if path: self.path=path
        if cols: self.cols=cols

    @cached_property
    def _data(self):  
        df=pd.read_csv(self.path)
        if self.fillna is not None: 
            df=df.fillna(self.fillna)
        return df
        
    @property
    def data(self):  
        df=self._data
        for c in self.cols_sep: df[c]=df[c].fillna('').apply(lambda x: str(x).split(self.sep))
        if self.cols: df=df[self.cols]
        return df



class Dwellings(Dataset):
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






class Members(Dataset):
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
    

    @cached_property
    def data(self):
        df=super().data.fillna('')
        df = df.merge(
            Dwellings().data,
            left_on='uri',
            right_on='member_uri',
            how='outer'
        ).drop('member_uri',axis=1).fillna('')

        df['member'] = df['uri'].apply(
            lambda x: x.split('/members/',1)[1][:-1] if '/members/' in x else ''
        )    
        
        # other
        df = df.set_index('member')
        return df
    





class Books(Dataset):
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
        'editor'
    ]
    

class Authors(Dataset):
    path:str = PATHS.get('authors') 

    



