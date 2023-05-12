from .imports import *



##################
##### PEOPLE #####
##################


def get_member_id(x): return x.split('/members/',1)[1][:-1] if '/members/' in x else ''

@cache
def get_members_df(with_dwellings=False): 
    df=get_urlpath_df('members').fillna('')
    df['is_expat'] = df['nationalities'].apply(lambda x: 'France' not in x)
    df['has_wikipedia'] = df['wikipedia_url']!=''
    df['has_viaf'] = df['viaf_url']!=''
    df['birth_decade'] = [str(x)[:3]+'0s' if x else '' for x in df['birth_year']]
    df['generation'] = df['birth_year'].apply(parse_generation)
    df['member_id']=df.uri.apply(get_member_id)
    df['nation'] = df['nationalities'].apply(lambda x: x.split(';')[0])

    df = df.set_index('member_id')

    if with_dwellings:
        from .dwellings import get_dwellings_df
        dfdw = get_dwellings_df()
        return df.merge(dfdw, on='member_id',how='outer')
    
    return df



    


def parse_generation(birth_year):
    if type(birth_year)!=float: return ''
    if (1883<=birth_year<=1900):
        return 'Lost Generation (1883-1900)'
    if (1901<=birth_year<=1927):
        return 'Greatest Generation (1901-1927)'
    return ''




def get_member_choices():
    df = get_members_df()

    choices = [
        # author name (sort alphabetically)
        get_select(df.sort_name, 'sort_name', 'Name', sort_by_value=True),
        
        
        
        # title
        get_select(df.title, 'title', 'Title', maxrows=5),

        # # age of author
        get_int_slider(df.birth_year, 'birth_year', 'Birth year'),
        get_int_slider(df.death_year, 'death_year', 'Death year'),

        
        # gender (sort alphabetically)
        get_select(df.gender, 'gender', 'Gender', sort_by_value=True),

        # nationality
        get_select(flatten_from(df.nationalities), 'nationalities_set', 'Nationality', sort_by_value=False),
        get_select(df.is_expat, 'is_expat', 'Is Expat?', sort_by_value=True),

        # membership
        get_select(flatten_from(df.membership_years), 'membership_years_set', 'Membership', sort_by_value=True),

        # arrond
        get_select(flatten_from(df.arrondissements), 'arrondissements_set', 'Arrondissements', sort_by_value=False),

        # expat
        get_select(df.has_card, 'has_card', 'Has Card?', sort_by_value=True),
        get_select(df.has_wikipedia, 'has_wikipedia', 'Has Wiki?', sort_by_value=True),
        get_select(df.has_viaf, 'has_viaf', 'Has VIAF?', sort_by_value=True),
        # gender (sort alphabetically)
        get_select(df.generation, 'generation', 'Generation', sort_by_value=False),

        
    ]
    return {ch.name:ch for ch in choices}


def parse_member_choices(choices):
    return parse_choices(
        choices,
        df=get_members_df()
    )
