from .imports import *



##################
##### PEOPLE #####
##################


def get_member_id(x): return x.split('/members/',1)[1][:-1] if '/members/' in x else ''

@cache
def get_members_df(): 
    df=get_urlpath_df('members').fillna('')
    df['is_expat'] = df['nationalities'].apply(lambda x: 'France' not in x)
    df['has_wikipedia'] = df['wikipedia_url']!=''
    df['has_viaf'] = df['viaf_url']!=''
    df['birth_decade'] = [str(x)[:3]+'0s' if x else '' for x in df['birth_year']]
    df['generation'] = df['birth_year'].apply(parse_generation)
    df['member_id']=df.uri.apply(get_member_id)
    return df.set_index('member_id')

