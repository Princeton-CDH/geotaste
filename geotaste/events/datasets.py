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

    @cached_property
    def data(self):
        df=super().data
        df['event']=[f'E{i+1:05}' for i in range(len(df))]
        return df.set_index('event')



class MemberEventsDataset(EventsDataset):
    cols_events = [
        'event_type',
        'start_date',
        'end_date'
    ]
    
    @cached_property
    def data(self):
        l=[]
        for event,row in super().data.iterrows():
            for member_uri in row['member_uris']:
                d={
                    'member':get_member_id(member_uri),
                    'book':get_book_id(row['item_uri']),
                    'event':event,
                    **dict(row)
                }
                l.append(d)
        return pd.DataFrame(l)

@cache
def MemberEvents(): return MemberEventsDataset()

@cache
def Events(): return EventsDataset()







class MemberEventDwellingsDataset(MemberEventsDataset):
    @cached_property
    def data(self, cols=['member','book','event','event_type','start_date','end_date','dwelling','dwelling_reason']):
        ld=[]
        df=super().data
        for i,row in df.iterrows():
            matches, reason = find_dwelling_ids(row)
            for match in matches:
                d={
                    'dwelling':match,
                    'dwelling_reason':reason,
                    'dwelling_numposs':len(matches),
                    **dict(row),
                }
                ld.append(d)
        return pd.DataFrame(ld)[cols]
    




def find_dwelling_ids(event_row, sep=DWELLING_ID_SEP, verbose=True, dispreferred = DISPREFERRED_ADDRESSES, cache=True):
    df = Dwellings().get_member(event_row.member)
    
    # if no dwelling at all?
    if not len(df): 
        return [''], '❓ No dwelling for member'
    
    # if only one?
    elif len(df)==1: 
        return list(df.index), '✅ Only one dwelling'
    
    
    # ok, if multiple:
    else:
        # try dispreferred caveats
        addresses = set(df.street_address)
        bad_address = list(addresses & set(DISPREFERRED_ADDRESSES.keys()))
        bad_address_str = ", ".join(bad_address)
        bad_address_reason = dispreferred[bad_address_str] if bad_address else ''
        df = df[~df.street_address.isin(dispreferred)]
        if len(df)==0: 
            return [''], f'❓ No dwelling after dispreferred filter ({bad_address_str} [{bad_address_reason}])'
        elif len(df)==1:
            return list(df.index), f'✅ One dwelling after dispreferred filter ({bad_address_str} [{bad_address_reason}])'
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
                if len(df)==0: return [''], '❓ No dwelling after time filter'
                elif len(df)==1: return list(df.index), '✅ One dwelling time filter'
                
                
            # Remove the non-Parisians?
            df = df[pd.to_numeric(df.dist_from_SCO,errors='coerce') < 50]  # less than 50km
            if len(df)==0: 
                return [''], f'❓ No dwelling after 50km filter'
            elif len(df)==1:
                return list(df.index), f'✅ One dwelling after 50km filter'
                
        return list(df.index), f'❌ {len(df)} dwellings after all filters'
        
