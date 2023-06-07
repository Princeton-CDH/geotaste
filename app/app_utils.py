
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
                        f'{minv}<={k}<={maxv}'
                        for minv,maxv in iter_minmaxs(v)
                    ]
                else:
                    qx = [
                        f'{k}=={vx}' if type(vx) in {int,float} else f'{k}=="{vx}"'
                        for vx in v
                    ]
            elif type(v)==str:
                qx=[f'{k}=="{v}"']
            
            if qx: ql.append(join_query(qx, operator='or'))
        q=join_query(ql, operator='and')        
    return q


def filter_df(df, filter_data={}, return_query=False):
    fd = {k:v for k,v in filter_data.items() if k in set(df.columns)}
    if not fd: return '' if return_query else df
    q=to_query_string(fd)
    if return_query: return q
    return df.query(q)