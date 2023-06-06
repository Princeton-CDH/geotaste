from app_imports import *
from app_figs import *


## Start app

app = Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    title='Geography of Taste',
)
server = app.server



## Set layout
WIDTH_SIDECOL=3

tabs_bar = dcc.Tabs([
        dcc.Tab(label="Members", value="members"),
        dcc.Tab(label="Books", value="books"),
        # dcc.Tab(label="Borrows", value="borrows"),
        dcc.Tab(label="Events", value="events"),
    ],
    className='tabs',
    value='members'
)

navbar = dbc.Navbar(
    dbc.Container([
        dbc.Row(
            [
                dbc.Col(
                    html.Img(src="/assets/SCo_logo_graphic.png", height="30px")
                ),
                dbc.Col(
                    dbc.NavbarBrand(
                        "Geography of Taste", 
                    ),
                ),
            ],
            align="center",
            style={'margin':'auto'},
        ),
    ]),
    color="light",
    dark=False,
)



### MEMBERS SIDE COL

"""
Text filter by name (type in name of member) and find out where they live.
Compare by gender
Compare by birth date
Membership date
Nationality
Arrondissement 
Ability to select multiple options
"""

gender_series = MemberDwellingsDataset().data.gender.replace({'':'(Unknown)'}).value_counts().index

sidecols = {}

sidecols['members'] = html.Div([
    html.H2('Members'),

    ## member search
    dbc.Label("Member name"),
    input_member := dbc.Input(type='search', list='member-datalist', placeholder='Select a member', debounce=True),
    html.Datalist(
        id='member-datalist', 
        children=[
            html.Option(value=x, label=y)
            for x,y in zip(Members().data.index, Members().data.name)
        ]
    ),
    html.Hr(),
    dbc.Label("Member gender"),
    input_gender := dbc.Checklist(
        options=gender_series,
        value=gender_series,
        switch=True,
    ),
], className='sidecol_members sidecol_showhide')

sidecols['books'] = html.Div([
    html.H2('Books'),
], className='sidecol_books sidecol_showhide')

sidecols['events'] = html.Div([
    html.H2('Events'),
], className='sidecol_events sidecol_showhide')




maincol = dbc.Col(
    width=9,
    class_name='maincol',
    children=[]
)

maincols = {}
maincols['members'] = html.Div([
    map_members := dcc.Graph(),
    tbl_members := dbc.Container()
], className='maincol_showhide')

maincols['books'] = html.Div([
    map_books := dcc.Graph(),
    tbl_books := dbc.Container()
], className='maincol_showhide')

maincols['events'] = html.Div([
    map_events := dcc.Graph(),
    tbl_events := dbc.Container()
], className='maincol_showhide')


### LAYOUT

app.layout = layout_container = dbc.Container([
    navbar_row := dbc.Row(navbar, class_name='navbar_row'),
    tabs_row := dbc.Row(tabs_bar, class_name='tabs_row'),
    content_row := dbc.Row(
        [
            sidecol := dbc.Col(list(sidecols.values()), width=3, class_name='sidecol'),
            maincol := dbc.Col(list(maincols.values()), width=9, class_name='maincol'),
        ], 
        class_name='content_row'
    )
])






@callback(
    [
        Output(map_members, 'figure'),
        # Output(tbl_members, 'children')
    ],
    [
        Input(input_member, 'value'),
        Input(input_gender, 'value'),
    ]
)
def set_members_data(member, genders):
    df = MemberDwellingsDataset().data.reset_index()
    if member: df=df[df.member.isin(member)]
    if genders: df=df[df.gender.isin(genders)]
    return plot_members_map(df)
    






## callbacks
SHOW = {'display':'block'}
HIDE = {'display':'none'}

@callback(
    [
        Output(sidecols['members'], component_property='style'),
        Output(maincols['members'], component_property='style')
    ],
    Input(tabs_bar, 'value')
)
def tab_switched_to_members(active_tab): 
    return [SHOW,SHOW] if active_tab=='members' else [HIDE,HIDE]

@callback(
    [
        Output(sidecols['books'], component_property='style'),
        Output(maincols['books'], component_property='style')
    ],
    Input(tabs_bar, 'value')
)
def tab_switched_to_books(active_tab): 
    return [SHOW,SHOW] if active_tab=='books' else [HIDE,HIDE]

@callback(
    [
        Output(sidecols['events'], component_property='style'),
        Output(maincols['events'], component_property='style')
    ],
    Input(tabs_bar, 'value')
)
def tab_switched_to_events(active_tab): 
    return [SHOW,SHOW] if active_tab=='events' else [HIDE,HIDE]



if __name__=='__main__':
    app.run(
        host='0.0.0.0', 
        debug=True,
        port=8052,
        # threaded=True,
        # dev_tools_ui=Fas,
        use_reloader=True,
        use_debugger=True,
        reloader_interval=1,
        reloader_type='watchdog'
    )

