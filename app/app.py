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
    dbc.Row([
        dbc.Col(
            html.H4("Filter by date of birth"),
            # width=11
        ),
        dbc.Col(
            button_clear_dob := dbc.Button(
                "Clear", 
                color="link", 
                n_clicks=0
            ),
            # width=1,
            style={'text-align':'right'}
        )
    ]),
    dbc.Row([
        graph_members_dob := dcc.Graph(figure=plot_members_dob()),
    ])
], body=True)

member_gender_card = dbc.Card([
    dbc.CardHeader("Filter by member gender"),
    dbc.CardBody(
        input_gender := dbc.Checklist(
            options=gender_series,
            value=[],
            switch=True,
        )
    )
])

member_filter_card = dbc.Card([
    dbc.CardHeader('Filter for members currently being applied'),
    dbc.CardBody(
        member_filter_pre := html.Pre('[none]')
    )
])

member_map_card = dbc.Card([
    dbc.CardHeader('Map of members’ apartments in Paris'), 
    dbc.CardBody(map_members := dcc.Graph(figure=plot_members_map()))
])

member_tbl_card = dbc.Card([
    dbc.CardHeader('Data on the filtered members'),
    dbc.CardBody(tbl_members := dbc.Container())
])


### LAYOUT

sidecol = dbc.Col(
    # width=6,
    class_name='sidecol',
    children=[
        member_name_card,
        member_dob_card,
        member_gender_card
    ]
)

offcanvas = dbc.Offcanvas(sidecol, is_open=False)
button_offcanvas = dbc.Button("Filter", n_clicks=0)

maincol = dbc.Col(
    # width=6,
    class_name='maincol',
    children=[
        member_filter_card,
        member_map_card,
        member_tbl_card,
    ]
)

storages = dbc.Container(
    store_member_filter := dcc.Store(id='filter_data')
)

app.layout = layout_container = dbc.Container([
    navbar_row := dbc.Row(navbar, class_name='navbar_row'),
    content_row := dbc.Row([
        offcanvas,
        button_offcanvas, 
        maincol
    ], class_name='content_row'),
    storages
])













### Callbacks


@app.callback(
    Output(offcanvas, "is_open"),
    Input(button_offcanvas, "n_clicks"),
    State(offcanvas, "is_open")
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

@callback(
    [
        Output(store_member_filter, "data", allow_duplicate=True),
        Output(graph_members_dob, "figure", allow_duplicate=True),
    ],
    Input(button_clear_dob, 'n_clicks'),
    [
        State(store_member_filter, "data"),
        State(graph_members_dob, 'figure'),
    ],
    prevent_initial_call=True
)
def clear_dob(n_clicks, filter_data, figdata):
    if not n_clicks or not filter_data: raise PreventUpdate
    if 'birth_year' in filter_data: filter_data.pop('birth_year')
    fig = plot_members_dob()
    return [filter_data,fig]







@callback(
    Output(store_member_filter, "data"),
    [
        Input(input_member, 'value'),
        Input(input_gender, 'value'),
        Input(graph_members_dob, 'selectedData'),
    ],
    State(store_member_filter, "data"),
)
def update_filter_from_dob(members, genders, selected_data, filter_data):
    if filter_data is None: filter_data = {}
    filter_data['member'] = members
    filter_data['gender'] = genders

    ## birth year
    if selected_data:
        try:
            minx,maxx = selected_data['range']['x']
            filter_data['birth_year'] = [(int(minx), int(maxx))]
        except Exception as e:
            sys.stderr.write(str(e))
            print('!!',e)

    return filter_data







@callback(
    [
        Output(member_filter_pre, 'children'),
        Output(map_members, 'figure'),
    ],
    Input(store_member_filter, "data"),
    State(map_members, 'figure'),
)
def update_pre_with_query_str(filter_data, fig_old):
    ff = FigureFactory(MemberDwellings().data)
    q = ff.filter_query(filter_data)
    df = ff.filter_df(q=q)
    # pre = f'{pformat(filter_data)}\nQ: {q}'
    pre = f'Q: {q}' if q else '[none]'
    fig_new = plot_members_map(df)
    fig = go.Figure(fig_new.data, go.Figure(fig_old).layout)
    return [pre,fig]



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

