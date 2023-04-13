from .imports import *


################
#### BOOKS #####
################

def get_book_id(x): return x.split('/books/',1)[1][:-1] if '/books/' in x else ''
@cache
def get_books_df(): 
    df=get_urlpath_df('books').fillna('')
    df['book_id']=df.uri.apply(get_book_id)
    return df.set_index('book_id')

