import pandas as pd
import numbers


def is_l(x): return type(x) in {list,tuple}
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


def filter_df(df, filter_data={}, return_query=False):

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




def is_numeric(x):
    return isinstance(x, numbers.Number)

def is_listy(x):
    return type(x) in {tuple,list}

def ensure_dict(x):
    if x is None: return {}
    if type(x) is dict: return x
    return dict(x)




def hasone(x:list, y:list):
    res = bool(set(x)&set(y))
    # print(['hasone',x,y,res])
    return res

def isin(x:object, y:list):
    res = bool(x in set(y))
    # print(['isin',x,y,res])
    return res

def isin_or_hasone(x:object, y:list):
    if type(x) in {list,set,tuple}:
        return hasone(x,y)
    else:
        return isin(x,y)
