from ..imports import *




class CombinedDataset(Dataset):
    path=PATHS.get('combined')
    fillna=''
    cols_creations = {
        'creator':'creator', 
        'creator_role':'creator_role',
    }
    cols_books = {
        'title':'book_title',
        'year':'book_year',
        'format':'book_format'
    }
    cols_members = {
        'sort_name':'member_sort_name',
        'title':'member_title',
        'gender':'member_gender',
        'birth_year':'member_birth_year',
        'death_year':'member_death_year',
        'membership_years':'member_membership_years',
        'nationalities':'member_nationalities'
    }
    cols_events = {
        'member':'member',
        'book':'book',
        'event':'event',
        'event_type':'event_type',
        'start_date':'event_start_date',
        'end_date':'event_end_date',
        'dwelling':'dwelling',
        # 'dwelling_numposs':'dwelling_numposs',
        'dwelling_reason':'dwelling_reason',
    }
    

    @cached_property
    def data(self, force=False):
        if force or not os.path.exists(self.path):
            # events and members (full outer join)
            events = selectrename_df(MemberEventDwellingsDataset().data, self.cols_events)
            # events = selectrename_df(MemberEvents().data, self.cols_events)
            members = selectrename_df(MembersDataset().data, self.cols_members)
            events_members = events.merge(members,on='member',how='outer').fillna(self.fillna)
            

            # creations and books (left join)
            creations = selectrename_df(CreationsDataset().data, self.cols_creations)
            books = selectrename_df(BooksDataset().data, self.cols_books)
            creations_books = creations.join(books)  # big to small, same index

            # all together (full outer join)
            odf = events_members.merge(creations_books, on='book', how='outer').fillna(self.fillna)
            odf.to_pickle(self.path)
            return odf
        else:
            return pd.read_pickle(self.path)
        