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


def _parse_circulation_years(cyearstr):
    return [int(cyr) for cyr in str(cyearstr).split(';') if cyr and str(cyr).isdigit()]

def get_book_choices():
    # Author filters
    df = get_books_df(with_author_data=False)

    all_circ_years = [x for l in df.circulation_years.apply(_parse_circulation_years) for x in l]

    choices = [
        # book name (sort alphabetically)
        get_dropdown(df.title, 'title', 'Title', sort_by_value=True),

        # age of author
        get_int_slider(all_circ_years, 'circulation_years', 'Circ. years')
    ]
    return {ch.name:ch for ch in choices}



def parse_book_choices(choices):
    df = get_books_df()
    df = parse_choices(choices, df, parse_sliders=False)

    ## circ years
    ok_years = choices['circulation_years']
    if ok_years.value != (ok_years.min, ok_years.max):
        ok_years_set = set(list(range(ok_years.value[0], ok_years.value[1]+1)))
        df = df[df.circulation_years.apply(lambda cyrstr: bool(set(_parse_circulation_years(cyrstr)) & ok_years_set))]
    return df