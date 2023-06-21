from .imports import *


##################
##### PEOPLE #####
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

    def __init__(self, path:str='', cols:list=[], **kwargs):
        if path: self.path=path
        if cols: self.cols=cols
        for k,v in kwargs.items(): setattr(self,k,v)

    @cached_property
    def data_orig(self):
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
        df=self.data_orig
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
            self.filter_key(key,vals)
            for key,vals in list(filter_data.items()) + list(other_filter_data.items())
        ])

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











