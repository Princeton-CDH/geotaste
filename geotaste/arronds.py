from .imports import *


# @cache
def get_geojson_arrondissement(force=False):
    url='https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson?lang=en&timezone=Europe%2FParis'
    fn=os.path.join(path_data,'arrondissements.geojson')
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



def get_arrond_counts(df,key='arrond_id'):
    arrond_counts = {n:0 for n in sorted(get_all_arrond_ids(), key=lambda x: int(x))}
    for k,v in dict(df[key].value_counts()).items(): arrond_counts[k]=v    
    arrond_df = pd.DataFrame([arrond_counts]).T.reset_index()
    arrond_df.columns=[key, 'count']
    arrond_df['perc']=arrond_df['count'] / sum(arrond_df['count']) * 100
    return arrond_df

