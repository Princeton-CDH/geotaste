from .imports import *
EMPTY_VAL='(none)'


def parse_choices(choices, df, parse_sliders=True):
    for key,choice in choices.items():
        if type(choice)==Dropdown and choice.value!='*':
            df = df[df[choice.name]==choice.value]

        elif parse_sliders and type(choice) in {widgets.IntRangeSlider}:
            minv,maxv = choice.value
            df[f'{choice.name}_q']=pd.to_numeric(
                df[choice.name], errors='coerce'
            )
            df = df.query(f'{minv} <= {choice.name}_q <= {maxv}')
    return df


def unique_vals(l, sort_by_count=True, sort_by_value=False, empty_val=EMPTY_VAL):
    l = [x if x!='' else empty_val for x in l]
    lset=set(l)
    ll=list(lset)
    if sort_by_value:
        return sorted(ll)
    elif sort_by_count:
        lcount=Counter(l)
        return sorted(ll, key=lambda word: lcount[word], reverse=True)
    else:
        return ll        
    
def get_dropdown(l, name='', desc='', sort_by_count=True, sort_by_value=False):
    opts = unique_vals(l, sort_by_count=sort_by_count, sort_by_value=sort_by_value)
    o = Dropdown(
        options=['*'] + opts,
        description=desc
    )
    o.name = name
    return o

def get_select(l, name='', desc='', sort_by_count=True, sort_by_value=False,maxrows=10):
    opts = unique_vals(l, sort_by_count=sort_by_count, sort_by_value=sort_by_value)
    o = widgets.SelectMultiple(
        options=opts,
        rows=len(opts) if len(opts)<maxrows else maxrows,
        description=desc
    )
    o.name = name
    return o

def get_int_slider(l, name='', desc=''):
    ## custom
    s = pd.to_numeric(l,errors='coerce')
    minval = int(s.min())
    maxval = int(s.max())
    
    birthyear_slider=widgets.IntRangeSlider(
        value=[minval, maxval],
        min=minval,
        max=maxval,
        step=1,
        description=desc
    )
    birthyear_slider.name=name
    return birthyear_slider



def show_choices(choices, header=''):
    printm(f'### {header}')
    for v in choices.values():
        display(v)



def flatten_from(l, sep=';', remove_empty=False):
    return [
        y 
        for x in l 
        for y in str(x).split(sep)
        if not remove_empty or y
    ]



def parse_choices(choices, df, parse_sliders=True, sep_set=';'):
    desc={}
    for key,choice in choices.items():
        name=choice.name
        value=choice.value
        if value==EMPTY_VAL: value=''

        if name.endswith('_set') and not name in set(df.columns):
            name_orig=name[:-4]
            df[name] = df[name_orig].apply(lambda x: set(x.split(sep_set)))

        if type(choice)==widgets.Dropdown and value!='*':
            df = df[df[name]==value]
            desc[name]=value

        elif type(choice)==widgets.SelectMultiple and value:
            value = tuple(['' if x==EMPTY_VAL else x for x in value])
            if name.endswith('_set'):
                df = df.loc[df[name].apply(lambda x: bool(set(x)&set(value)))]
            else:
                df = df[df[name].isin(set(value))]
            desc[name]=value

        elif parse_sliders and type(choice) in {widgets.IntRangeSlider}:
            minv,maxv = choice.value
            if (minv,maxv) != (choice.min, choice.max):
                df[f'{choice.name}_q']=pd.to_numeric(
                    df[choice.name], errors='coerce'
                )
                df = df.query(f'{minv} <= {choice.name}_q <= {maxv}')
                desc[name]=value
    return df, desc



