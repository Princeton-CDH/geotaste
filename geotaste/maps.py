from .imports import *

def get_choices():
    df=get_combined_df()
    counts = df.book_id.value_counts()
    books = sorted(list(set(df.book_id)), key=lambda x: -counts[x])
    book_choice = Dropdown(options=['*'] + books)
    event_choice = Dropdown(options=['*'] + sorted(list(set(df.event_type))))
    year_choice = Dropdown(options=['*'] + sorted(list(set(df.start_dec))))
    return (book_choice, event_choice, year_choice)


def get_mapdf(book=None, event='borrow', year=None):
    figdf = get_combined_df()
    if book and book!='*': figdf = figdf[figdf.book_id == book]
    if event and event!='*': figdf = figdf[figdf.event_type.str.lower() == event.lower()]
    if year and year!='*': figdf = figdf[figdf.start_dec == year]

    def get_arinsee(x):
        for y in str(x).split(';'):
            if y.strip().isdigit():
                return str(y.strip())
    figdf['arrond_id']=figdf.arrondissements.apply(get_arinsee)
    return figdf

def get_heatmap(book=None, event=None, year=None):
    figdf=get_mapdf(book=book,event=event,year=year)
    return draw_heatmap(figdf)
    
def filter_figdf(figdf):
    figdf['lat']=pd.to_numeric(figdf['lat'], 'coerce')
    figdf['lon']=pd.to_numeric(figdf['lon'], 'coerce')
    return figdf[figdf.lat.notna() & figdf.lon.notna()]

def draw_map(figdf,zoom=True,**kwargs):
    figdf=filter_figdf(figdf)
    centroid = latlon_SCO
    opts=dict(location=centroid, zoom_start=13, width='90%')
    if not zoom: opts={**opts, **dict(zoom_control=False, scrollWheelZoom=False, dragging=False)}
    opts={**opts, **kwargs}
    map = folium.Map(**opts)
    return map

def draw_heatmap(figdf,zoom=True,**kwargs):
    figdf=filter_figdf(figdf)
    # display(figdf[['lat','lon']])
    map = draw_map(figdf[['lat','lon']],zoom=zoom,**kwargs)
    hmap = folium.plugins.HeatMap(figdf[['lat','lon']])
    hmap.add_to(map)
    return map
    

def i_heatmap():
    book_choice,event_choice,year_choice = get_choices()
    return interact(
        get_heatmap,
        book=book_choice, 
        event=event_choice, 
        year=year_choice
    )





def get_points(df): return df[['lat','lon']].values



def compare_maps(map1,map2,width=600,height=600,return_str=False,**kwargs):
    iframe1 = get_iframe(map1,width=width,height=height,return_str=True,float='left',**kwargs)
    iframe2 = get_iframe(map2,width=width,height=height,return_str=True,**kwargs)
    ostr=iframe1 + iframe2
    return ostr if return_str else HTML(ostr)




def compare_heatmaps(df1,df2,width=600,height=400,**kwargs):
    hmap1=draw_heatmap(df1,**kwargs)
    hmap2=draw_heatmap(df2,**kwargs)
    return compare_maps(hmap1,hmap2,width=width,height=height)




def get_iframe(map, width=600, height=400, return_str=False, **attrs):
    src=map.get_root().render().replace('"', '&quot;')
    
    styled_default=dict(
        # display='inline-block',
        # width='49%',
        margin='0 auto',
        border='0',
    )
    
    styled = {**styled_default, **attrs}
    stylestr = '; '.join(f'{k}:{v}' for k,v in styled.items())
    ostr=f'<iframe srcdoc="{src}" width="{width}" height="{height}" style="{stylestr}"></iframe>'
    return ostr if return_str else HTML(ostr)


def compare_maps(map1,map2,width=600,height=600,return_str=False,**kwargs):
    iframe1 = get_iframe(map1,width=width,height=height,return_str=True,float='left',**kwargs)
    iframe2 = get_iframe(map2,width=width,height=height,return_str=True,float='right',**kwargs)
    ostr=iframe1 + iframe2
    return ostr if return_str else HTML(ostr)

def draw_choropleth(
        df, 
        heatmap=True, 
        key='arrond_id', 
        value='count', 
        count_df=None, 
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        **kwargs):
    df = filter_figdf(df)
    hmap=draw_heatmap(df,**kwargs) if heatmap else draw_map(df,**kwargs)
    cdf=get_arrond_counts(df) if count_df is None else count_df
    cmap = folium.Choropleth(
        get_geojson_arrondissement(),
        data=cdf,
        columns=[key, value],
        key_on="feature.id",
        fill_color=fill_color,
        fill_opacity=fill_opacity,
        line_opacity=line_opacity,
    )
    
    cdfi=cdf.set_index(key)
    vkeys=set()
    for s in cmap.geojson.data['features']:
        for k,v in dict(cdfi.loc[s['id']]).items():
            vkeys.add(k)
            s['properties'][k] = round(float(v),2)
        
    # and finally adding a tooltip/hover to the choropleth's geojson
    folium.GeoJsonTooltip([key]+list(vkeys)).add_to(cmap.geojson)
    cmap.add_to(hmap)

    return hmap


def get_col_choice(col, sort_by_count=False, description=''):
    DF=get_borrow_df()
    counts = DF[col].value_counts()
    books = sorted(list(set(DF[col])), key=lambda x: -counts[x] if sort_by_count else x)
    book_choice = Dropdown(
        options=['*'] + books, 
        description=col if not description else description,
    )
    book_choice.name=col
    return book_choice

def get_book_choice():
    return get_col_choice('item_title', description='Book')
def get_member_choice():
    return get_col_choice('member_sort_names', description='Member')
def get_author_choice():
    return get_col_choice('item_authors', description='Author')
def get_decade_choice():
    return get_col_choice('start_dec', description='Decade')
def get_gender_choice():
    return get_col_choice('gender', description='M. gender')
def get_nation_choice():
    return get_col_choice('nation', description='M. nationality')
def get_expat_choice():
    return get_col_choice('is_expat', description='M. is expat')

def get_fame_choice():
    return get_col_choice('has_wikipedia', description='M. has wikipedia')





def get_df_from_choices(choices):
    df=get_borrow_df()
    for x in choices:
        if x.value and x.value!='*':
            df = df[df[x.name] == x.value]
    return df

def get_choice_desc(choices):
    l=[]
    for x in choices:
        if x.value!='' and x.value!='*':
            l.append(x.name+': '+str(x.value))
    return '; '.join(l) if l else '(All borrow events)'

def get_choice_funcs():
    return [
        get_decade_choice, 
        get_author_choice, 
        get_book_choice, 
        get_member_choice, 
        get_gender_choice, 
        get_expat_choice,
        get_nation_choice, 
        get_fame_choice
    ]

@cache
def get_choices_left():
    return [f() for f in get_choice_funcs()]
@cache
def get_choices_right():
    return [f() for f in get_choice_funcs()]

def draw_maps(e=None):
    df1=get_df_from_choices(get_choices_left())
    df2=get_df_from_choices(get_choices_right())
    desc1=get_choice_desc(get_choices_left())
    desc2=get_choice_desc(get_choices_right())
    with get_out():
        clear_output()
        display(HTML(f'''
            <div style="float:left; color:#1A5276;"><h2>{desc1} (in blue in third map)</h2></div>
            <div style="float:right; color:#7B241C"><h2>{desc2} (in red in third map)</h2></div>
            <div style="clear:both;">&nbsp;</div>
            <hr/>
        '''))
        compare_choropleths(df1,df2)

# # def get_layout():
# #     button=Button(description='Draw maps')
# #     button.on_click(draw_maps)
# #     return HBox([
# #         VBox([Label('Left-hand map')]+get_choices_left()),
# #         VBox([Label('Right-hand map')]+get_choices_right()),
# #         button
# #     ])

# def show_layout():
#     display(get_layout())


# @cache
# def get_out(): return Output()

# def show_comparator():
#     show_layout()
#     draw_maps()
#     display(get_out())


def compare(): 
    clear_output()
    show_comparator()





#####


def parse_generation(birth_year):
    if type(birth_year)!=float: return ''
    if (1883<=birth_year<=1900):
        return 'Lost Generation (1883-1900)'
    if (1901<=birth_year<=1927):
        return 'Greatest Generation (1901-1927)'
    return ''


def get_coords_from_arrond(coords_col, arrond_col):
    coords = []
    for coord,arrond in zip(coords_col,arrond_col):
        coord_l = coord.split(';')
        arrond_l = arrond.split(';')
        assert len(coord_l) == len(arrond_l)
        for i,x in enumerate(arrond_l):
            if x: break
        coord_x = coord_l[i]
        coords.append(coord_x)
    return coords

def get_arinsee(x):
    for y in str(x).split(';'):
        if y.strip().isdigit():
            return str(y.strip())

def get_coords_df(df):
    df = df[df.coordinates!='']
    df['coord'] = get_coords_from_arrond(df.coordinates, df.arrondissements)
    df['arrond_id']=df.arrondissements.apply(get_arinsee)
    def get_lat(coord): return float(coord.split(',')[0]) if coord else np.nan
    def get_lon(coord): return float(coord.split(',')[1]) if coord else np.nan
    df['lat'] = df.coord.apply(get_lat)
    df['lon'] = df.coord.apply(get_lon)
    # valid coords
    df = df.loc[ df[['lat','lon']].dropna().index ]
    return df

def get_member_data_choices():
    df=get_coords_df(get_members_df().fillna(''))

    genders = Dropdown(options=['* Member Gender *'] + sorted(list(set(df.gender))))
    is_expat = Dropdown(options=['* Member: Is Expat? *'] + sorted(list(set(df.is_expat))))
    nats = Dropdown(options=['* Member Nationality *'] + sorted(list(set([nat.strip() for nats in df.nationalities for nat in nats.split(';')]))))
    
    has_wikipedia = Dropdown(options=['* Member: Has wikipedia? (is famous?) *'] + sorted(list(set(df.has_wikipedia))))
    has_viaf = Dropdown(options=['* Member: Has VIAF? (is author?) *'] + sorted(list(set(df.has_viaf))))
    
    
    
    return {
        'gender':genders,
        'is_expat':is_expat,
        'nationality':nats,
        'has_wikipedia':has_wikipedia,
        'has_viaf':has_viaf,
    }













@cache
def get_member_choices_left():
    return get_member_data_choices()
@cache
def get_member_choices_right():
    return get_member_data_choices()

def get_member_df_from_choices(choice_d):
    df = get_members_df()
    cols = set(df.columns)
    choice_d = get_active_choice_d(choice_d)
    for k,v in choice_d.items():
        if k in cols:
            print(k,v)
            df = df[df[k]==v]    
    
    # others
    nat = choice_d.get('nationality')
    if nat:
        df = df[df['nationalities'].str.contains(nat)]    
    
    return df

def get_active_choice_d(choice_d):
    od={}
    for k,v in choice_d.items():
        vstr=str(v.value)
        if vstr and vstr[0]!='*':
            od[k]=v.value
    return od

def get_member_choice_desc(choice_d):
    choice_d=get_active_choice_d(choice_d)
    if choice_d: return '; '.join(f'{x}: {y}' for x,y in choice_d.items())
    return '(All members)'

def draw_member_maps(e=None):
    df1=get_coords_df(get_member_df_from_choices(get_member_choices_left()))
    df2=get_coords_df(get_member_df_from_choices(get_member_choices_right()))
    desc1=get_member_choice_desc(get_member_choices_left())
    desc2=get_member_choice_desc(get_member_choices_right())
    with get_out():
        clear_output()
        compare_choropleths(df1,df2, desc1=desc1, desc2=desc2)
        
def compare_choropleths(df1,df2,return_str=False,desc1='',desc2='',**kwargs):
    opts={**dict(zoom_start=12, zoom=True, heatmap=True, value='perc'), **kwargs}
    df1 = filter_figdf(df1)
    df2 = filter_figdf(df2)

    m1=draw_choropleth(df1, **opts)
    m2=draw_choropleth(df2, **opts)
    
    ## diff
    cdf1=get_arrond_counts(df1).set_index('arrond_id')
    cdf2=get_arrond_counts(df2).set_index('arrond_id')
    diff_df = (cdf1-cdf2)
    
    odf=pd.DataFrame()
    for c in cdf1: 
        odf[c+'_L']=cdf1[c]
        odf[c+'_R']=cdf2[c]
        odf[c+'_L-R']=diff_df[c]
    odf=odf.sort_values('perc_L-R')
    
    diff_opts = {**opts}
    diff_opts['heatmap']=False
    diff_opts['fill_color']='RdBu'
    m3=draw_choropleth(df1, count_df=diff_df.reset_index(), **diff_opts)
    
    htmlstr = ''
    if desc1 or desc2:
        htmlstr += f'''
            <hr/>
            <h3>Juxtaposition of left and right maps</h3>
            <div style="float:left; color:#1A5276;"><h4>L: {desc1}</h4> (n={len(df1)}, {odf.count_L.sum()} in arrondissement)</div>
            <div style="float:right; color:#7B241C"><h4>R: {desc2}</h4> (n={len(df2)}, {odf.count_R.sum()} in arrondissement)</div>
            <div style="clear:both;"></div>
        '''
    htmlstr+= compare_maps(m1,m2,return_str=True, height=400, width=600)
    htmlstr+= f'''
        <div style="clear:both";>
            <br/>
            <hr/>
            <h3>Comparison table and contrast map</h3>
            <i>Below is a table of counts and percentages creating the two maps, (L)eft and (R)ight, above. 
            <br/>It also shows the (L-R) values: negative here means (R) outweighed left; positive means (L) outweighed (R).
            <br/>In the map below and right, red means that (R) outweighed (L); blue means (L) outweighed (R).
            </i>
        </div>
        <div style="clear:both";>
            {get_iframe(m3,return_str=True, height=400, width=600, float="right")}
            <div style="width:400px;">{round(odf,1).to_html()}<br/></div>
        </div>'
    '''
    
    display(HTML(htmlstr))
    return htmlstr if return_str else HTML(htmlstr)

def get_layout(choices_left_d={}, choices_right_d={}, **kwargs):
    button=Button(description='Draw maps')
    button.on_click(draw_member_maps)
    return HBox([
        VBox([Label('Left-hand map')]+list(get_member_choices_left().values())),
        VBox([Label('Right-hand map')]+list(get_member_choices_right().values())),
        button
    ])

def show_layout(*args,**kwargs):
    display(get_layout(*args,**kwargs))


@cache
def get_out(): return Output()

def show_comparator():
    show_layout()
    draw_member_maps()
    display(get_out())


def compare(): 
    clear_output()
    show_comparator()

