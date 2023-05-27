from app_imports import *
import dash_mantine_components as dmc


def get_paper(children=[], className='',**kwargs):
    return dmc.Paper(
        children=children,
        **{
            **dict(
                shadow="md",
                radius='sm',
                # withBorder=True,
                className='paper '+className
            ),
            **kwargs
        }
    )


def get_header():
    return get_paper(
        children=[
            html.H1(TITLE),
            html.P(children=[
                "The ",
                dcc.Link("Shakespeare & Co Project", href='https://shakespeareandco.princeton.edu/'),
                " uses the lending library records... Below are filters for the map to the right. Who borrowed what when where among expats in early 20th century Paris?"
            ]),
        ]
    )

def get_side_col():
    return dmc.Col(
        children=[
            get_header(),
            get_members_panel(),
            get_books_panel(),
            get_events_panel(),
        ],
        className='layout-side-col grid-col',
        span=4,
    )

def get_main_col():
    return dmc.Col(
        className='layout-main-col grid-col',
        children=[
            get_paper(get_map_tabs()),
            # get_paper(get_map_table())
        ],
        span=8,
        
    )

def get_tbl_col():
    return dmc.Col(
        className='layout-tbl-col grid-col',
        children=[
            get_map_table(),
        ],
        span=8,
    )

def get_member_map_and_table():
    return dmc.Stack([
        get_paper(get_map_graph()),
        get_paper(get_map_table())
    ], className='map-table-stack')

def get_map_tabs():
    tabs = dmc.Tabs(
         children=[
            dmc.TabsList(
                children=[
                    dmc.Tab("Map people", value="tab-map-people"),
                    dmc.Tab("Map events", value="tab-map-events"),
                ]
            ),
            dmc.TabsPanel(get_member_map_and_table(), value="tab-map-people"),
            dmc.TabsPanel(dmc.Text('ok'), value="tab-map-events"),
        ],
        value="tab-map-people",
        className='map-tabs'
    )
    return tabs


def get_layout_root():
    return dmc.Grid(
        className='layout-grid',
        children=[
            get_side_col(),
            get_main_col(),
            # get_tbl_col()
        ],
        gutter="xs",
        # grow=True
    )

def get_app_layout():
    return dmc.MantineProvider(
        theme={
            "fontFamily": "'Inter', sans-serif",
            "primaryColor": "indigo",
            "components": {
                "Button": {"styles": {"root": {"fontWeight": 400}}},
                "Alert": {"styles": {"title": {"fontWeight": 500}}},
                "AvatarGroup": {"styles": {"truncated": {"fontWeight": 500}}},
            },
        },
        inherit=True,
        withGlobalStyles=True,
        withNormalizeCSS=True,
        children=[get_layout_root()]
    )

