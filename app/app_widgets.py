from app_imports import *


# def get_dropdown(
#         options=[], 
#         value=None,
#         id=None,
#         sort_alpha=False, 
#         default=[], 
#         input_type=dcc.Dropdown,
#         **kwargs):
#     if id is None and hasattr(series,'name'): id=series.name
#     assert id is not None

#     # get options
#     if type(options) is pd.Series:
#         opts = list(options.value_counts().index) if not sort_alpha else list(sorted(set(options)))
#         opts = [str(x) for x in opts]
#         options = [dict(label=x if x!='' else '(empty)', value=x) for x in opts]
#     elif type(options) is list and options and type(options[0])!=dict:
#         options = [dict(label=x, value=x) for x in options]

#     drop = input_type(
#         id=id,
#         options=options,
#         value=value if value is not None else default,
#         **kwargs
#     )
#     return drop

# def get_labeled_dropdown(*args, label='', **kwargs):
#     dropdown = get_dropdown(*args, **kwargs)
#     return get_labeled_element(dropdown, label)


# def get_labeled_slider(series, label='', step=10, id=None):
#     s = pd.to_numeric(series, errors='coerce')
#     slider = dcc.RangeSlider(
#         id=id,
#         min=s.min() // step * step,
#         max=s.max() // step * step + step,
#         step=step,
#         marks=None,
#         tooltip={"placement": "bottom", "always_visible": True}
#     )
#     return get_labeled_element(slider, label)


# def get_labeled_checklist(*x,**y):
#     y['input_type']=dcc.Checklist
#     return get_labeled_dropdown(*x,**y)









def get_label_str(x, label_d={}):
    return label_d.get(
        x,
        label_d.get(
            str(x),
            str(x).title() if x not in {'',None} else '[?]'
        )
    )

def get_options(data, sort_alpha=False, label_d={}):
    if type(data)==pd.Series:
        s=data.fillna('').apply(str).value_counts()
        data = [
            (f"{get_label_str(key, label_d=label_d)} ({count:,})", key) 
            for key,count in zip(s.index, s)
        ]
    else:
        data = [
            (
                (get_label_str(x, label_d=label_d), x) 
                if type(x) not in {list,tuple} 
                else x
            )
            for x in data
        ]
    return data


    
    
    return data

def get_radio_group(data=[], label='', value='', label_d={}, **kwargs):
    return dmc.RadioGroup(
        [dmc.Radio(label, value=value) for label, value in get_options(data,label_d={})],
        value=value,
        label=label,
        size="sm",
        mt=10,
        className='widget-group'
    )

def get_labeled_element(element, label=''):
    if not label:
        label = element.id.replace('_',' ').title() + ('?' if element.id.startswith('is_') else '')
    
    from app_layout import get_paper
    return get_card(
        children=[
            dmc.Text(label, className='mantine-InputWrapper-label'),
            element
        ],
        className='widget-group',
        shadow='xs',
        radius=0,
        withBorder=False
    )

def get_card(children=[], className='', **kwargs):
    className+=' card'
    return dmc.Card(
        children=children,
        className=className,
        **{
            **dict(
                shadow='xs', 
                withBorder=True,
                radius=10

            ),
            **kwargs
        }
    )


def get_chip_group(data=[], label='',label_d={},multiple=True,**kwargs):
    return get_labeled_element(
        dmc.ChipGroup([
            dmc.Chip(
                l,
                value=v,
                variant="filled",
            )
            for l,v in get_options(data,label_d=label_d)
            ],
            multiple=multiple,
            spacing=5,
            **kwargs
        ),
        label=label
    )
    






## Is expat?
def get_is_expat():
    return get_chip_group(
        id='is_expat',
        data=get_members_df().is_expat,
        label="Is the member an expat?",
        label_d={'True':'Yes', 'False':'No'}
    )

def get_member_gender():
    return get_chip_group(
        id='member-gender',
        data=get_members_df().gender,
        label='Gender',
    )

def get_member_nation():
    return get_chip_group(
        data=pd.Series([nat for nations in get_members_df().nationalities for nat in nations.split(';')]),
        value=[],
        id='member-nation',
        label='Nationality of member'
    )


def get_range_slider(series, label='', step=10, value=None,**kwargs):
    s = pd.to_numeric(series, errors='coerce')
    minval=s.min() // step * step
    maxval=s.max() // step * step + step
    value=value if value is not None else [minval,maxval]
    slider = dmc.RangeSlider(
        min=minval,
        max=maxval,
        value=value,
        step=step,
        labelAlwaysOn=True,
        mt=35,
        className='slider',
        **kwargs
    )
    return get_labeled_element(slider, label=label)



def get_member_dob():
    return get_range_slider(
        get_members_df().birth_year, 
        id='member-birth_year',
        label='Birth year'
    )

def get_member_generation():
    return get_chip_group(
        get_members_df().generation,
        id='member-generation',
        label='Member generation',
        label_d={'':'[Other]'}
    )

def get_member_has_wikipedia():
    return get_chip_group(
        get_members_df().has_wikipedia,
        label_d={
            'True':'Yes',
            'False':'No'
        },
        label='Member has a wikipedia page?'

    )

# get_labeled_checklist(
#     get_members_df().generation,
#     id='generation'
# ),

# get_labeled_checklist(
#     get_members_df().has_wikipedia,
#     id='has_wikipedia',
#     inline=True
# ),

# get_labeled_checklist(
#     get_members_df().has_viaf,
#     id='has_viaf',
#     inline=True
# ),



def get_members_panel():
    from app_layout import get_paper
    return get_paper(
        children=[
            dmc.Title('Members', order=3),
            get_member_gender(),
            get_member_dob(),
            get_member_generation(),
            get_is_expat(),
            # get_member_nation(),
            get_member_has_wikipedia()
        ],
    )