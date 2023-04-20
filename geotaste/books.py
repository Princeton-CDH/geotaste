from .imports import *


################
#### BOOKS #####
################

def get_book_id(x): return x.split('/books/',1)[1][:-1] if '/books/' in x else ''
@cache
def get_books_df(with_author_data=True): 
    df=get_urlpath_df('books').fillna('')
    df['book_id']=df.uri.apply(get_book_id)
    df['book_dec'] = [str(x)[:3]+'0s' if x else '' for x in df['year'].fillna('')]
    df['first_author'] = [str(x).split(';')[0] for x in df.author.fillna('')]
    
    
    ## merge with authors?
    if with_author_data:
        df_au = get_authors_df()
        df = df.merge(
            df_au, 
            left_on='first_author', 
            right_on='author_sort_name', 
            how='left', 
            suffixes=('', '_au')
        )

    return df.set_index('book_id')

