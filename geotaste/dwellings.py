from .imports import *


def get_utm_df(lats, lons): 
    import utm, numpy as np, pandas as pd

    o = []
    for lat,lon in zip(lats,lons):
        try:
            res = utm.from_latlon(lat,lon)
            odx = {
                'utm_easting':res[0],
                'utm_northing':res[1],
                'utm_zone_number':res[2],
                'utm_zone_letter':res[3]
            }
        except Exception as e:
            odx = {}
        o.append(odx)
    return pd.DataFrame(o)

def geodist(latlon1, latlon2=latlon_SCO, unit='km'):
    from geopy.distance import distance
    import numpy as np
    try:
        dist = distance(latlon1, latlon2)
        return getattr(dist,unit)
    except Exception:
        return np.nan

def get_dwelling_id(row):
    o=f'{row.member_id} DWELT AT {row.street_address.replace(" ","-")}'
    if row.start_date: o+=f' FROM {row.start_date}'
    if row.end_date: o+=f' UNTIL {row.end_date}'
    return o
    
@cache
def get_dwellings_df(): 
    df=get_urlpath_df('dwellings').fillna('')
    startcols = ['member_id','start_date','end_date']
    endcols = [c for c in df if c.endswith('_id')]
    df['member_id']=df.member_uri.apply(get_member_id)
    odf=df[startcols + [c for c in df if c not in set(startcols+endcols)] + endcols]
    odf['dwelling_id'] = odf.apply(get_dwelling_id, axis=1)
    odf['lat']=odf.latitude.apply(lambda x: float(x) if x else np.nan)
    odf['lon']=odf.longitude.apply(lambda x: float(x) if x else np.nan)
    odf['arrond_id']=odf.arrrondissement.apply(lambda x: str(int(x)) if x else '')

    odf['dist_from_SCO'] = [round(geodist((lat,lon), unit='km'), 3) for lat,lon in zip(odf.lat, odf.lon)]

    return odf.set_index('dwelling_id').sort_values('dist_from_SCO')
    
@cache
def get_dwelling_cache():
    from sqlitedict import SqliteDict
    cache_fn = os.path.join(path_data,'dwelling_id_cache.sqlitedict')
    ensure_dirname(cache_fn)
    return SqliteDict(cache_fn)

def find_dwelling_id(event_row, sep=DWELLING_ID_SEP, verbose=True, dispreferred = DISPREFERRED_ADDRESSES, cache=True):
    
    if cache: 
        sqd = get_dwelling_cache()
        res = sqd.get(event_row.name)
        if res is None:
            res = find_dwelling_id(
                event_row,
                sep=sep,
                verbose=verbose,
                dispreferred=dispreferred,
                cache=False
            )
            sqd[event_row.name] = res
            sqd.commit()
        return res
    else:
        
        memid = event_row.member_id

        df_dwellings = get_dwellings_df()
        df = df_dwellings[df_dwellings.member_id==memid].sort_values('dist_from_SCO')
        
        # if no dwellign at all?
        if not len(df): 
            return '', '❓ No dwelling at all'
        
        # if only one?
        elif len(df)==1: 
            return df.index[0], '✅ Only one dwelling'
        
        
        # ok, if multiple:
        else:
            # try dispreferred caveats
            addresses = set(df.street_address)
            bad_address = list(addresses & set(DISPREFERRED_ADDRESSES.keys()))
            bad_address_str = ", ".join(bad_address)
            bad_address_reason = dispreferred[bad_address_str] if bad_address else ''
            df = df[~df.street_address.isin(dispreferred)]
            if len(df)==0: 
                return '', f'❓ No dwelling after dispreferred filter ({bad_address_str} [{bad_address_reason}])'
            elif len(df)==1:
                return df.index[0], f'✅ One dwelling after dispreferred filter ({bad_address_str} [{bad_address_reason}])'
            else:
                # if start date?
                borrow_start = event_row.start_date
                borrow_end = event_row.end_date

                if borrow_start and borrow_end:
                    if borrow_start:
                        # If we know when the borrow began, then exclude dwellings which end before that date
                        df = df[df.end_date.apply(lambda x: not (x and x[:len(borrow_start)]<borrow_start))]
                    if borrow_end:
                        # If we know when the borrow ended, then exclude dwellings which begin after that date
                        df = df[df.start_date.apply(lambda x: not (x and x[:len(borrow_end)]>borrow_end))]
                    
                    # No longer ambiguous?
                    if len(df)==0: return '', '❓ No dwelling after time filter'
                    elif len(df)==1: return df.index[0], '✅ One dwelling time filter'
                    
                    
                # Remove the non-Parisians?
                df = df[df.dist_from_SCO < 50]  # less than 50km
                if len(df)==0: 
                    return '', f'❓ No dwelling after 50km filter'
                elif len(df)==1:
                    return df.index[0], f'✅ One dwelling after 50km filter'
                    
            return sep.join(df.index), '❌ Multiple dwellings after all filters'
            

def find_dwellings_for_member_events(df, sep=DWELLING_ID_SEP):
    from tqdm import tqdm
    tqdm.pandas(desc='Finding appropriate dwelling ID for events')
    idf = df.reset_index()
    dwell = get_dwellings_df()
    odf = pd.DataFrame([
        {
            'dwelling_id':resx.split(sep)[0],
            'dwelling_ids':resx.split(sep),
            'dwelling_id_reason':reasonx,
            **{('dwelling_'+k if k in set(idf.columns) else k):v for k,v in (dict(dwell.loc[resx.split(sep)[0]]) if resx else {}).items()}
        } 
        for resx,reasonx 
        in idf.progress_apply(find_dwelling_id, axis=1)
    ])
    return pd.concat([idf,odf], axis=1)