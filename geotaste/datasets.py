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
    
    















