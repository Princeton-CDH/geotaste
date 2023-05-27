from app_imports import *

##################################################
# DATA
##################################################


@cache
def get_total_data_members():
    print('getting total_data_members')
    return filter_figdf(get_members_df(with_dwellings=True))

@cache
def get_total_data_events():
    # df = get_combined_filtered_events_from_choices()
    print('getting total_data_events')
    df = pd.read_pickle(os.path.join(heredir,'data.pkl'))
    return filter_figdf(df).merge(get_members_df(), on='member_id')


## Filtering
def get_filtered_data_members(map_kind='all'): 
    map_kind=str(map_kind).lower()
    if 'all' in map_kind:
        return get_total_data_members()
    elif 'without' in map_kind:
        df1=get_total_data_members()
        df2=get_total_data_events()
        does_have_records = set(df2.member_id)
        return df1[~df1.member_id.isin(does_have_records)]
    else:
        return get_total_data_events()


