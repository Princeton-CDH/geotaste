from app_imports import *
from app_figs import *
from app_widgets import *


## Start app

app = Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    title='Geography of Taste',
)
server = app.server



## Set layout
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
df_members = Members().data

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


member_name_card = dbc.Card([
    html.H4("Select members by name"),

    input_member := dcc.Dropdown(
        options = [dict(value=idx, label=lbl) for idx,lbl in zip(Members().data.index, Members().data.sort_name)],
        value = [],
        multi=True,
        placeholder='Select individual members'
    )
], body=True)



member_dob_card = dbc.Card([
    html.H4("Filter by date of birth"),
    graph_members_dob := dcc.Graph(figure=plot_members_dob())
], body=True)

member_gender_card = dbc.Card([
    html.H4("Filter by member gender"),
    input_gender := dbc.Checklist(
        options=gender_series,
        value=gender_series,
        switch=True,
    ),
], body=True)




sidecols['members'] = html.Div([
    # html.H3('Members'),
    member_name_card,
    member_dob_card,
    member_gender_card,

    # html.Hr(),

    # dbc.Label('Date of birth'),
    
    
    

    


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


member_map_card = dbc.Card([
    html.H4('Map of members’ apartments in Paris'), 
    map_members := dcc.Graph()
], body=True)

member_tbl_card = dbc.Card([
    html.H4('Data on the filtered members'), 
    tbl_members := dbc.Container()
], body=True)

maincols = {}
maincols['members'] = html.Div([
    
    ,

    dbc.Card(, body=True)
], className='maincol_showhide')

maincols['books'] = html.Div([
    map_books := dcc.Graph(),
    tbl_books := dbc.Container()
], className='maincol_showhide')

maincols['events'] = html.Div([
    map_events := dcc.Graph(),
    tbl_events := dbc.Container()
], className='maincol_showhide')

# shared_cols = set(maincols.keys()) & set(sidecols.keys())
shared_cols = {'members'}


### LAYOUT

app.layout = layout_container = dbc.Container([
    navbar_row := dbc.Row(navbar, class_name='navbar_row'),
    content_row := dbc.Row([
        dbc.Row([
            dbc.Col(sidecols[col], width=6, class_name='sidecol'),
            dbc.Col(maincols[col], width=6, class_name='maincol'),
        ], class_name=f'datatype_container datatype_container_{col}') 
        for col in shared_cols
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
        # Input(input_gender, 'value'),
    ]
)
def set_members_data(member):
    df = MemberDwellingsDataset().data.reset_index()
    if member: df=df[df.member.isin(member)]
    # if genders: df=df[df.gender.isin(genders)]
    
    fig = plot_members_map(df)
    return fig
    


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

