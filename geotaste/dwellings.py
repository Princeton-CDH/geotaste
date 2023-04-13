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
    



def find_dwelling_id(event_row, sep=DWELLING_ID_SEP, verbose=True, dispreferred = DISPREFERRED_ADDRESSES):
    memid = event_row.member_id
    df_dwellings = get_dwellings_df()
    df = df_dwellings[df_dwellings.member_id==memid].sort_values('dist_from_SCO')
    
    # if no dwellign at all?
    if not len(df): 
        return '', '❓ No dwelling at all'
    
    # if only one?
    elif len(df)==1: 
        return df.index[0], '✅ Only one dwelling'
    
    ## @TODO: 
    # Prefer Paris, prefer French, ...
        
    
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

            dwelling_starts = df.start_date
            dwelling_ends = df.end_date
            never_dwelling = not any(dwelling_starts)

            ###
            if not borrow_start and borrow_end:
                return sep.join(df.index), '❌ Multiple dwellings after dispreferred filter (no event time info)'
            elif never_dwelling:
                return sep.join(df.index), '❌ Multiple dwellings after dispreferred filter (no dwelling time info)'
            else:
                if borrow_start:
                    # If we know when the borrow began, then exclude dwellings which end before that date
                    df = df[df.end_date.apply(lambda x: not (x and x[:len(borrow_start)]<borrow_start))]
                if borrow_end:
                    # If we know when the borrow ended, then exclude dwellings which begin after that date
                    df = df[df.start_date.apply(lambda x: not (x and x[:len(borrow_end)]>borrow_end))]
                
                # No longer ambiguous?
                if len(df)==0: return '', '❓ No dwelling after time filter'
                elif len(df)==1: return df.index[0], '✅ One dwelling after time filter'
                else: # Still ambiguous
                    df = df[~df.street_address.isin(dispreferred)]
                    if len(df)==0: return '', '❓ No dwelling after time and dispreferred filter'
                    elif len(df)==1: return df.index[0], '✅ One dwelling after time and dispreferred filter'
                    else:
                        return sep.join(df.index), '❌ Multiple dwellings after time and dispreferred filter'
            

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
    return pd.concat([idf[['event_id','member_id','book_id','event_type', 'start_date', 'end_date']],odf], axis=1)