from .imports import *


################
#### AUTHORS #####
################

def get_author_id(x): return ''.join(y for y in x if y.isalpha() or y==' ').lower().replace(' ','-')
@cache
def get_authors_df():
    df=get_urlpath_df('authors').fillna('').drop('gender',1)
    df.columns = [f'author_{str(col).lower().replace(" ","_")}' for col in df.columns]
    df['author_id']=df['author_sort_name'].apply(get_author_id)
    
    df['author_is_expat'] = df['author_nationality'].apply(lambda x: 'France' not in x)
    # df['has_wikipedia'] = df['wikipedia_url']!=''
    # df['has_viaf'] = df['viaf_url']!=''
    df['author_birth_decade'] = [str(x)[:3]+'0s' if x else '' for x in df['author_birth_year']]

    from .people import parse_generation
    df['author_generation'] = df['author_birth_year'].apply(parse_generation)
    
    return df.set_index('author_id')

def get_author_choices():
    from .choices import get_dropdown, get_int_slider

    # Author filters
    df = get_authors_df()

    choices = [
        # author name (sort alphabetically)
        get_select(df.author_name, 'author_name', 'Name', sort_by_value=True),
        
        # gender (sort alphabetically)
        get_select(df.author_gender, 'author_gender', 'Gender', sort_by_value=True),

        # nationality
        get_select(df.author_nationality, 'author_nationality', 'Nationality'),

        # language
        get_select(df.author_language, 'author_language', 'Language'),

        # age of author
        get_int_slider(df.author_birth_year, 'author_birth_year', 'Birth year')
    ]
    return {ch.name:ch for ch in choices}



def parse_author_choices(choices):
    from .choices import parse_choices

    return parse_choices(
        choices,
        get_authors_df()
    )

def show_author_choices(choices):
    printm('### Author choices')
    for v in choices.values():
        display(v)