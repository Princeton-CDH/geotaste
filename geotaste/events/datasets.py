from ..imports import *




class EventsDataset(Dataset):
    url:str = URLS.get('events')
    path:str = PATHS.get('events')
    cols:list = [
        'event_type',
        'start_date',
        'end_date',
        'member_uris',
        'member_names',
        'member_sort_names',
        'subscription_price_paid',
        'subscription_deposit',
        'subscription_duration',
        'subscription_duration_days',
        'subscription_volumes',
        'subscription_category',
        'subscription_purchase_date',
        'reimbursement_refund',
        'borrow_status',
        'borrow_duration_days',
        'purchase_price',
        'currency',
        'item_uri',
        'item_title',
        'item_volume',
        'item_authors',
        'item_year',
        'item_notes',
        'source_type',
        'source_citation',
        'source_manifest',
        'source_image'
    ]

    cols_sep:list = [
        'member_uris', 
        'member_names', 
        'member_sort_names'
    ]

    


class CombinedDataset(Dataset):
    @cached_property
    def data(self):
        df_events=EventsDataset().data
        new_l = []
        for i,row in df_events.iterrows():
            book = row.item_uri.split('/books/',1)[1][:-1] if '/books/' in row.item_uri else ''
            for member_uri in row.member_uris:
                member = member_uri.split('/members/',1)[1][:-1] if '/members/' in member_uri else ''
                new_row = {
                    'member':member,
                    'book':book,
                    **{k:v for k,v in row.items() if k.split('_')[0] not in {'member','item'}}
                }
                new_l.append(new_row)
        new_df = pd.DataFrame(new_l)
        return new_df.merge(
            CreationsDataset().data, on = 'book', how='outer', suffixes=('_combined','')
        ).merge(
            MembersDataset().data, on = 'member', how='outer', suffixes=('_combined','')
        ).set_index('member')




@cache
def Events(): return EventsDataset()

@cache
def Combined(): return CombinedDataset()