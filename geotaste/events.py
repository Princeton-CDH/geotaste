from .imports import *



#################
#### EVENTS #####
#################

def get_event_id(row):
    base=f'{row.member_id} {(row.event_type+"s").upper()} {row.book_id}'
    if not row.start_date: return base
    if row.end_date and row.start_date!=row.end_date:
        return f'{base} FROM {row.start_date} TO {row.end_date}'
    return f'{base} ON {row.start_date}'

@cache
def get_events_df(): 
    # get as exists
    df = get_urlpath_df('events').fillna('')
    
    ## expand by semi colon!
    def getrowinfo(row, i):
        odx={}
        for k,v in dict(row).items():
            if ';' in str(v):
                vs = str(v).split(';')
                v=vs[i]
            odx[k]=v
        return odx
    
    df_events_expanded = pd.DataFrame(
        {**getrowinfo(row,mi), 'member_uri':muri, 'member_id':get_member_id(muri), 'book_id':get_book_id(row.item_uri)}
        for i,row in df.iterrows()
        for mi,muri in enumerate(row.member_uris.split(';'))
    )
    
    odf = df_events_expanded[['member_id','book_id']+[col for col in df if not col.split('_')[0] in {'member','item'}]]
    odf['event_id'] = odf.apply(get_event_id,axis=1)
    odf['start_dec'] = odf.start_date.apply(lambda x: str(x)[:3]+'0' if str(x) else '?')
    
    # odf['dwelling_ids'] = odf.apply(lambda row: find_dwelling_id(row, verbose=False), axis=1)
    return odf.set_index('event_id')



def get_event_dwelling_id(row):
    return f'{row.event_id} WHILE {row.dwelling_id}'

@cache
def get_event_dwellings_df(lim=None):
    df_events = get_events_df().iloc[:lim]
    odf = find_dwellings_for_member_events(df_events)
    odf['event_dwelling_id'] = odf.apply(get_event_dwelling_id, axis=1)
    return odf.set_index('event_dwelling_id')



def get_event_choices():
    df = get_events_df()

    choices = [
        get_select(df.event_type, name='event_type', desc='Event type'),
        get_select(df.borrow_status, name='borrow_status', desc='Borrow status'),
        get_int_slider(df.subscription_duration_days, 'subscription_duration_days', 'subscription_duration_days'),
        
        get_date_picker(name='start_date_min', desc='Start (min)'),
        get_date_picker(name='start_date_max', desc='Start (max)'),

        get_date_picker(name='end_date_min', desc='End (min)'),
        get_date_picker(name='end_date_max', desc='End (max)'),
        
    ]
    return {ch.name:ch for ch in choices}


def parse_event_choices(choices):
    df = get_events_df()
    df,desc = parse_choices(choices, df)
    return df,desc

