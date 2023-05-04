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

