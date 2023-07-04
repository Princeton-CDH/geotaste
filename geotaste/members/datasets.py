from ..imports import *

### datasets


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
        df['member'] = df['uri'].apply(
            lambda x: x.split('/members/',1)[1][:-1] if '/members/' in x else ''
        )
        df['membership_years'] = [[int(y) for y in x if y] for x in df['membership_years']]
        df['gender']=df['gender'].replace({'':'Unknown'})
        
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
    cols_rename:dict = {
        'start_date':'dwelling_start_date',
        'end_date':'dwelling_end_date',
    }
    cols_q = [
        'latitude',
        'longitude',
    ]

    @cached_property
    def data(self):
        df=super().data
        df['arrond_id']=df['arrrondissement'].apply(lambda x: '' if not x else str(int(x)))
        return df


class MemberDwellingsDataset(Dataset):
    
    @staticmethod
    def add_dwellings(df_members):
        df_dwellings = DwellingsDataset().data
        return df_members.reset_index().merge(
            df_dwellings,
            left_on='uri',
            right_on='member_uri',
            how='inner'
        ).drop('member_uri',axis=1).set_index('member')

    @cached_property
    def data(self):        
        return self.add_dwellings(MembersDataset().data)



@cache
def Members(): return MembersDataset()
@cache
def MemberDwellings(): return MemberDwellingsDataset()
