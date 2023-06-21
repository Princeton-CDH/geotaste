from .imports import *




def hasone(x:list, y:list):
    res = bool(set(x)&set(y))
    # print(['hasone',x,y,res])
    return res

def isin(x:object, y:list):
    res = bool(x in set(y))
    # print(['isin',x,y,res])
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
    return type(x) in {tuple,list}

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







def describe_filters(store_data, records_name='records'):
    if not store_data or not INTENSION_KEY in store_data or not EXTENSION_KEY in store_data:
        return ''

    def format_intension(d):
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
            o=f'_{o}_ on  `{key}`'
            ol.append(o)
        return "; ".join(ol)

    len_ext=len(store_data[EXTENSION_KEY])
    fmt_int=format_intension(store_data[INTENSION_KEY])
    return f'Filtering {fmt_int} yields _{len_ext}_ {records_name}.'


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
        if key in keys_both: return 'Both'
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