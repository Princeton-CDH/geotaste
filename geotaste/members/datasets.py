from ..imports import *

### datasets

def get_member_id(uri):
    return uri.split('/members/',1)[1][:-1] if '/members/' in uri else ''

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

    @cached_property
    def data(self):
        df=super().data
        df['member'] = df['member_uri'].apply(get_member_id)
        df['arrond_id']=df['arrrondissement'].apply(lambda x: 'X' if not x else str(int(x)))
        df['dist_from_SCO'] = [
            round(geodist(latlon, LATLON_SCO, unit='km'), 3) 
            for latlon in zip(df.latitude, df.longitude)
        ]
        df['dwelling'] = df.apply(get_dwelling_id, axis=1)
        df=df.drop_duplicates(['member','city','street_address','arrond_id','start_date','end_date'])
        return df.fillna('').set_index('dwelling')

    def get_member(self, member):
        return self.data[self.data['member'] == member]
    


class MemberDwellingsDataset(Dataset):
    
    @staticmethod
    def add_dwellings(df_members):
        df_dwellings = DwellingsDataset().data
        return df_members.reset_index().merge(
            df_dwellings,
            on='member',
            # how='outer',
            suffixes=('_member','')
        ).drop('member_uri',axis=1).set_index('member').fillna('?')

    @cached_property
    def data(self):        
        return self.add_dwellings(Members().data)



@cache
def Members(): return MembersDataset()
@cache
def MemberDwellings(): return MemberDwellingsDataset()
@cache
def Dwellings(): return DwellingsDataset()




def get_dwelling_id(row):
    o=f'{row.member.upper()} dwelt in {row.city.upper()}'
    if row.arrond_id and is_valid_arrond(row.arrond_id): 
        o+=f' in the {ordinal_str(int(row.arrond_id)).upper()}'
    if row.street_address: o+=f' ({row.street_address})'
    if row.start_date: o+=f' from {row.start_date}'
    if row.end_date: o+=f' until {row.end_date}'
    return o