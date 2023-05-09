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
        get_select(df.title, 'title', 'Title', sort_by_value=True),
        get_select(df.format, 'format', 'Format', sort_by_value=False),
        get_select(df.uncertain, 'uncertain', 'Uncertain?', sort_by_value=False),
        get_select(df.editor, 'editor', 'Editor', sort_by_value=False, maxrows=5),
        get_select(df.translator, 'translator', 'Translator', sort_by_value=False, maxrows=5),
        get_select(df.introduction, 'introduction', 'Intro by', sort_by_value=False, maxrows=5),

        get_int_slider(all_circ_years, 'circulation_years', 'Circ. years'),
        get_int_slider(df.year, 'year', "Pub year"),

        get_int_slider(df.event_count, 'event_count', "Event count"),
        get_int_slider(df.borrow_count, 'borrow_count', "Borrow count"),

        
    ]
    return {ch.name:ch for ch in choices}

def parse_book_choices(choices):
    df = get_books_df()
    df,desc = parse_choices(choices, df, except_keys={'circulation_years'})
    ok_years = choices.get('circulation_years')
    if ok_years is not None and ok_years.value != (ok_years.min, ok_years.max):
        ok_years_set = set(list(range(ok_years.value[0], ok_years.value[1]+1)))
        df = df[df.circulation_years.apply(lambda cyrstr: bool(set(_parse_circulation_years(cyrstr)) & ok_years_set))]
        desc['circulation_years']=ok_years.value

    
    return df,desc


def show_book_choices():
    choices = get_book_choices()
    show_choices(choices, 'Book options')
    return choices