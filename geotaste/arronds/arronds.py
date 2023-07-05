from ..imports import *

## geojson/arrond utils

def get_geojson_arrondissement(force=False):
    import os,json,requests
    
    # download if nec
    url=URLS.get('geojson_arrond')
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


@cache
def get_all_arrond_ids():
    ids_in_geojson = {
        d['id'] 
        for d in get_geojson_arrondissement()['features']
    }
    return {n for n in ids_in_geojson if n and n.isdigit() and n!='99'}# | {'X','?','99'} # outside of paris + unkown

def get_arrond_counts_series(df_or_series,key='arrond_id'):
    arrond_counts = {n:0 for n in get_all_arrond_ids()}
    series=df_or_series[key] if type(df_or_series) is pd.DataFrame else df_or_series
    counts=dict(series.value_counts())
    combined = {**arrond_counts, **counts}
    def sort_index(index):
        def sortranker(v): return int(v) if v.isdigit() else np.inf
        return pd.Series(index).apply(sortranker)
    return pd.Series(combined,name=key).sort_index(key=sort_index)

def get_arrond_counts(df,key='arrond_id'):
    arrond_counts = {n:0 for n in sorted(get_all_arrond_ids(), key=lambda x: int(x) if x.isdigit() else np.inf)}
    for k,v in dict(df[key].value_counts()).items(): arrond_counts[k]=v    
    arrond_df = pd.DataFrame([arrond_counts]).T.reset_index()
    arrond_df.columns=[key, 'count']
    arrond_df = arrond_df.set_index(key).loc[filter_valid_arrond]
    arrond_df['perc']=arrond_df['count'] / sum(arrond_df['count']) * 100
    return arrond_df
    

def compare_arrond_counts(df_L, df_R):
    df_arronds_L = get_arrond_counts(df_L)
    df_arronds_R = get_arrond_counts(df_R)
    df_arronds_diff = df_arronds_R - df_arronds_L
    odf=pd.DataFrame()
    for c in df_arronds_diff:
        odf[c+'_L']=df_arronds_L[c]
        odf[c+'_R']=df_arronds_R[c]
        odf[c+'_L->R']=df_arronds_diff[c]
    odf=odf.sort_values('perc_L->R')
    return odf


def is_valid_arrond(x):
    return bool(str(x).isdigit()) and bool(x!='99')

def filter_valid_arrond(df):
    return (df.index.str.isdigit()) & (df.index!='99')