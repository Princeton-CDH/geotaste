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
    return {
        d['id'] 
        for d in get_geojson_arrondissement()['features']
    }

def get_arrond_counts_series(df,key='arrond_id'):
    arrond_counts = {n:0 for n in sorted(get_all_arrond_ids(), key=lambda x: int(x))}
    for k,v in dict(df[key].value_counts()).items(): arrond_counts[k]=v    
    return pd.Series(arrond_counts).sort_index()

def get_arrond_counts(df,key='arrond_id'):
    arrond_counts = {n:0 for n in sorted(get_all_arrond_ids(), key=lambda x: int(x))}
    for k,v in dict(df[key].value_counts()).items(): arrond_counts[k]=v    
    arrond_df = pd.DataFrame([arrond_counts]).T.reset_index()
    arrond_df.columns=[key, 'count']
    arrond_df['perc']=arrond_df['count'] / sum(arrond_df['count']) * 100
    return arrond_df.set_index(key)

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