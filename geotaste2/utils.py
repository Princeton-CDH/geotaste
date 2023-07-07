from .imports import *




def hasone(x:list, y:list):
    res = bool(set(x)&set(y))
    return res

def isin(x:object, y:list):
    res = bool(x in set(y))
    return res

def isin_or_hasone(x:object, y:list):
    if not is_listy(y): 
        y={y}
    else:
        y=set(y)
    if type(x) in {list,set,tuple}:
        return hasone(x,y)
    else:
        return isin(x,y)




def is_numeric(x):
    return isinstance(x, numbers.Number)

def is_listy(x):
    return type(x) in {tuple,list,pd.Series}

def ensure_dict(x):
    if x is None: return {}
    if type(x) is dict: return x
    return dict(x)






def is_l(x): return type(x) in {list,tuple,set}
def iter_minmaxs(l):
    if is_l(l):
        for x in l:
            if is_l(x):
                if len(x)==2 and not is_l(x[0]) and not is_l(x[1]):
                    yield x
                else:
                    yield from iter_minmaxs(x)


def to_query_string(filter_data={}):
    def join_query(ql, operator='and'):
        if len(ql)>1:
            q=f' {operator} '.join(f'({qlx})' for qlx in ql)
        elif len(ql)==1:
            q=ql[0]
        else:
            q=''
        return q

    # preproc/clean
    if not filter_data: filter_data={}
    for k,v in list(filter_data.items()):
        if v is None:
            del filter_data[k]    
    
    # something there?
    q=''
    if filter_data:
        ql=[]
        for k,v in filter_data.items():
            qx=''
            if is_l(v):
                if v and is_l(v[0]):
                    qx = [
                        f'{minv} <= {k} <= {maxv}'
                        for minv,maxv in iter_minmaxs(v)
                    ]
                else:
                    qx = [
                        f'{k} == {vx}' if type(vx) in {int,float} else f'{k} == "{vx}"'
                        for vx in v
                    ]
            elif type(v)==str:
                qx=[f'{k}=="{v}"']
            
            if qx: ql.append(join_query(qx, operator='or'))
        q=join_query(ql, operator='and')        
    return q


def filter_df_extensionally(df:pd.DataFrame, filter_data:dict):
    # print(type(df), df)
    intersection = set(df.index) & set(filter_data[EXTENSION_KEY].keys())
    odf = df.loc[list(intersection)].sample(frac=1)

    ## add any new info
    stored_info = {infotype for objid,objvald in filter_data[EXTENSION_KEY].items() for infotype in objvald.keys()}
    # for new_col in (stored_info - set(df.columns)):
    for new_col in stored_info:
        odf[new_col] = [filter_data[EXTENSION_KEY].get(objid,{}).get(new_col) for objid in odf.index]
    
    return odf
    

def filter_df(df, d, ik=INTENSION_KEY, ek=EXTENSION_KEY):
    if not d: return df
    if ek in d: return filter_df_extensionally(df, d)
    raise Exception

def filter_df_old(df, filter_data={}, return_query=False):

    fd = {
        k:v 
        for k,v in filter_data.items() 
        if k in set(df.columns)
    }
    if not fd: return '' if return_query else df
    q=to_query_string(fd)
    if return_query: return q
    if not q: return df
    
    
    
    ## do query ...
    # print('\n\n\n\n#### FILTERING: #### \n\n')
    # print(df)
    # print('fd',fd)
    # print('q',q)
    
    # ensure quant cols!
    q_cols = {
        k 
        for k,v in fd.items()
        if (
            (is_numeric(v))
            or 
            (is_listy(v) and v and is_numeric(v[0]))
            or (is_listy(v) and v and is_listy(v[0]) and v[0] and is_numeric(v[0][0]))
        )
    }
    # print('q_cols',q_cols)
    
    df = df.sample(frac=1)
    for qcol in q_cols:
        df[qcol] = pd.to_numeric(df[qcol], errors='coerce')

    # print(df)

    odf = df.query(q)
    # print(odf)

    # for key in fd:
    #     print(df[key])
    #     print(q)
    #     print(odf[key])

    return odf




def format_intension(d, empty=BLANK):
    ol=[]
    for key,l in d.items():
        is_quant = all(is_numeric(x) for x in l)
        if len(l)<3:
            o = ' and '.join(str(x) for x in l)
        elif is_quant:
            # l.sort()
            o=f'{l[0]} to {l[-1]}'
        else:
            # o=' and '.join(f'{repr(x)}' for x in l)
            o=f'{l[0]} ... {l[-1]}'
        # o=f'_{o}_ on  *{key}*'
        o=f'{o} in {key}'
        ol.append(o)
    return "; ".join(ol) if ol else empty


def describe_filters(store_data, records_name='records'):
    if not store_data or not INTENSION_KEY in store_data or not EXTENSION_KEY in store_data:
        return ''
    len_ext=len(store_data[EXTENSION_KEY])
    fmt_int=format_intension(store_data[INTENSION_KEY])
    return fmt_int
    # return f'Filtering {fmt_int} yields _{len_ext:,}_ {records_name}.'
    # return f'{fmt_int} -> {len_ext:,} {records_name}'


def first(x, default=None):
    for y in x: return y
    return default


def intersect_filters(*filters_d, ik=INTENSION_KEY, ek=EXTENSION_KEY):
    filters_d=[d for d in filters_d if d and ik in d and ek in d]
    if not filters_d: return {}
    
    outd = {ik:{},ek:{}}    
    key_sets = []
    for fd in filters_d:
        outd[ik]={**outd[ik], **fd[ik]}
        key_sets.append(set(fd[ek].keys()))
    shared_keys = set.intersection(*key_sets)
    for key in shared_keys: outd[ek][key]={}
    for fd in filters_d:
        for key in fd[ek]:
            if key in shared_keys:
                outd[ek][key]={**outd[ek][key], **fd[ek][key]}
    return outd


def compare_filters(filter_data_L, filter_data_R, key_LR='L_or_R'):
    keys_L = set(filter_data_L.get('extension',{}).keys())
    keys_R = set(filter_data_R.get('extension',{}).keys())

    keys_L_only = keys_L - keys_R
    keys_R_only = keys_R - keys_L
    keys_both = keys_L & keys_R
    keys_either = keys_L | keys_R

    def get_key_type(key):
        if key in keys_L_only: return 'L'
        if key in keys_R_only: return 'R'
        if key in keys_both: return 'L&R'
        return 'Neither'
    
    outd = {INTENSION_KEY:{}, EXTENSION_KEY:{}}
    outd[INTENSION_KEY] = (
        filter_data_L.get(INTENSION_KEY,{}), 
        filter_data_R.get(INTENSION_KEY,{})
    )
    outd[EXTENSION_KEY] = {
        str(key):{
            key_LR:get_key_type(key),
            **filter_data_L.get(EXTENSION_KEY,{}).get(key,{}),
            **filter_data_R.get(EXTENSION_KEY,{}).get(key,{})
        } for key in keys_either
    }
    return outd

def filter_series(
        series, 
        vals = [], 
        test_func = isin_or_hasone,
        series_name=None,
        matches = []):
    key = series.name if series_name is None else series_name
    if matches:
        series_matching = series[[m for m in matches if m in set(series.index)]]
    elif not vals:
        series_matching = series
    else:
        series_matching = series[series.apply(lambda x: test_func(x, vals))]
    
    o = {
        INTENSION_KEY:{key:vals},
        EXTENSION_KEY:{objid:({key:objval}) for objid,objval in dict(series_matching).items()}
    }
    return o

def combine_figs(fig_new, fig_old):
    fig_old = go.Figure(fig_old) if type(fig_old)!=go.Figure else fig_old
    return go.Figure(
        layout=fig_old.layout if fig_old is not None and hasattr(fig_old,'data') and fig_old.data else fig_new.layout,
        data=fig_new.data
    )



def flatten_list(s):
    l=[]
    for x in s:
        if is_listy(x):
            l+=flatten_list(x)
        else:
            l+=[x]
    return l

def flatten_series(s):
    s=pd.Series(s)
    l=[]
    for i,x in zip(s.index, s):
        if is_listy(x):
            l+=[(i,xx) for xx in flatten_list(x)]
        else:
            l+=[(i,x)]
    il,xl=zip(*l)
    return pd.Series(xl,index=il)


def make_counts_df(series):
    return pd.DataFrame(
        pd.Series(
            (x if x!='' else UNKNOWN for x in flatten_list(series))
        , name=series.name).value_counts()
    ).reset_index()


def delist_df(df, sep=' '):
    def fix(y):
        if is_listy(y): return sep.join(str(x) for x in y)
        if is_numeric(y): y=round(y,2)
        return y
    df=df.copy()
    for col in df:
        df[col]=df[col].apply(fix)
    return df


def get_dash_table(df, cols=[], page_size=25, height_table='80vh', height_cell=60):
    cols=list(df.columns) if not cols else [col for col in cols if col in set(df.columns)]
    dff = delist_df(df[cols])
    cols_l = [{'id':col, 'name':col.replace('_',' ').title()} for col in cols]
    return dash_table.DataTable(
        data=dff.to_dict('records'),
        columns=cols_l,
        sort_action="native",
        sort_mode="multi",
        filter_action="native",
        page_action="native",
        # page_action="none",
        page_size=page_size,
        fixed_rows={'headers': True},
        style_cell={
            'minWidth': 95, 'maxWidth': 95, 'width': 95,
        },

        style_data={
            'minHeight': height_cell, 'maxHeight': height_cell, 'height': height_cell,
            'whiteSpace': 'normal',
        },
        style_table={
            'height':height_cell * 12, 
            'overflowY':'auto',
            # 'display':'block',
            # 'flex-didrection':'column',
            # 'flex-grow':1,
            # 'width':'100%',
            # 'border':'1px solid #eeeee'
        },
    )


def ordinal_str(n: int) -> str:
    """
    derive the ordinal numeral for a given number n
    """
    return f"{n:d}{'tsnrhtdd'[(n//10%10!=1)*(n%10<4)*n%10::4]}"





def get_tabs(children=[], active_tab=None, tab_level=1, **kwargs):
    return dbc.Tabs(
        children=[dbc.Tab(**d) for d in children], 
        active_tab=active_tab if active_tab else (children[0].get('tab_id') if children else None), 
        id=dict(type=f'tab_level_{tab_level}', index=int(time.time())),
        **kwargs
    )

def force_int(x, errors=0):
    try:
        return int(x)
    except ValueError:
        return errors
    



class CachedData:
    def __init__(self, *x, path_cache=None, **y):
        self.path_cache = os.path.join(PATH_DATA, path_cache) if path_cache and not os.path.isabs(path_cache) else path_cache

    def cache(self, tablename='unnamed', flag='c', autocommit=True, **kwargs):
        from sqlitedict import SqliteDict
        return SqliteDict(
            filename=self.path_cache, 
            tablename=tablename, 
            flag=flag,
            autocommit=autocommit,
            **kwargs
        )
    






def measure_dists(
        series1, 
        series2, 
        methods = [
            'braycurtis', 
            'canberra', 
            'chebyshev', 
            'cityblock', 
            'correlation', 
            'cosine', 
            'euclidean', 
            'jensenshannon', 
            'minkowski', 
        ],
        series_name='dists',
        calc = ['median']
        ):
    from scipy.spatial import distance
    a=pd.Series(series1).values
    b=pd.Series(series2).values
    o=pd.Series({fname:getattr(distance,fname)(a,b) for fname in methods}, name=series_name)
    for fname in calc: o[fname]=o.agg(fname)
    return o



def combine_LR_df(dfL, dfR):
    allL,allR = set(dfL.index),set(dfR.index)
    L,R,both = allL-allR,allR-allL,allR&allL
    return pd.concat([
        dfL.loc[list(L)].assign(L_or_R='L'),
        dfL.loc[list(both)].assign(L_or_R='L&R'),
        dfR.loc[list(R)].assign(L_or_R='R'),
    ])


def serialize_d(d):
    return tuple(d.items())

def unserialize_d(d):
    return dict(d)


def nowstr():
    from datetime import datetime
    current_datetime = datetime.now()
    friendly_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return friendly_string


from loguru import logger
class Logmaker:
    def log(self, *x, level='debug', **y):
        o=' '.join(str(xx) for xx in x)
        name=self.__class__.__name__
        if hasattr(self,'name'): name+=f' ({self.name})'
        o = f'[{nowstr()}] {name}: {o}'
        f=getattr(logger,level)
        f(o)




def get_filter_data(filter_data={}):
    if filter_data and not EXTENSION_KEY in filter_data:
        x=set(filter_data.keys()) - set(MembersDataset.cols)
        if x:
            print(f'!! using CombinedDataset due to {x} !!')
            filter_data = Combined().filter(**filter_data)
        else:
            print('using MembersDataset')
            filter_data = Members().filter(**filter_data)
    return filter_data




def selectrename_df(df, col2col={}):
    return df[col2col.keys()].rename(columns=col2col)





def geodist(latlon1, latlon2, unit='km'):
    from geopy.distance import distance
    import numpy as np
    try:
        dist = distance(latlon1, latlon2)
        return getattr(dist,unit)
    except Exception:
        return np.nan
    





def qualquant_series(series, quant=False):
    series=pd.Series(series) if type(series)!=pd.Series else series
    if quant is True: 
        series=pd.to_numeric(series, errors='coerce')
    elif quant is False:
        series=series.fillna('').apply(str).replace({'':UNKNOWN})
    return series
    