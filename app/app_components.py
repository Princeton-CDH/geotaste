from typing import Any
from app_imports import *
from app_figs import *


class SimpleCard(dbc.Card):
    def __init__(self, body=[], header=[], footer=[]):
        children = []
        if header: children+=[dbc.CardHeader(header)]
        if body: children+=[dbc.CardBody(body)]
        if footer: children+=[dbc.CardFooter(footer)]
        super().__init__(children, outline=True)




class MemberNameCard(DashComponent):
    def layout(self, params=None):
        return SimpleCard(
            body=[self.input_member],
            header=['Select members by name']
        )

    @cached_property
    def input_member(self):
        return dcc.Dropdown(
        options = [dict(value=idx, label=lbl) for idx,lbl in zip(Members().data.index, Members().data.sort_name)],
        value = [],
        multi=True,
        placeholder='Select individual members'
    )


class MemberDOBCard(DashComponent):
    @cached_property
    def store(self): return dcc.Store(id=f'store__{self.name}')

    def layout(self, params=None):
        return SimpleCard(
            header = [
                "Filter by date of birth | ",
                self.button_clear,
                ],
            body = [
                self.graph,
                self.store,
                self.filter_desc,
            ],
        )
    
    @cached_property
    def filter_desc(self): return html.Div()

    @cached_property
    def graph(self):
        return dcc.Graph(figure=self.plot())
    
    def ff(self, filter_data={}):
        return MemberFigureFactory(filter_data)

    def plot(self, filter_data={}, ff=None):
        return self.ff(filter_data).plot_dob()

    @cached_property
    def button_clear(self):
        return dbc.Button(
            "Clear", 
            color="link", 
            n_clicks=0
        )
    
    def component_callbacks(self, app):

        @app.callback(
            Output(self.store, "data"),
            Input(self.graph, 'selectedData'),
            State(self.store, "data"),
        )
        def update_selection(selected_data, filter_data):
            if filter_data is None: filter_data = {}
            if selected_data:
                try:
                    minx,maxx = selected_data['range']['x']
                    filter_data['birth_year'] = [(int(minx), int(maxx))]
                except Exception as e:
                    pass
            return filter_data
        
        @app.callback(
            [
                Output(self.store, "data", allow_duplicate=True),
                Output(self.graph, "figure", allow_duplicate=True),
            ],
            Input(self.button_clear, 'n_clicks'),
            prevent_initial_call=True
        )
        def clear_selection(n_clicks):
            return {}, self.plot()
        
        @app.callback(
            Output(self.filter_desc, 'children'),
            Input(self.store, 'data')
        )
        def f(filter_data, key='birth_year'):
            df0 = self.ff().df
            df = self.ff(filter_data).df
            res = filter_data.get(key)
            minv,maxv = df0[key].dropna().apply(int).min(), df0[key].dropna().apply(int).max()
            
            if res:
                obj = res[0]
                if len(obj)==2:
                    minv,maxv = obj
            return dcc.Markdown(f'Selecting members born between **{minv}** and **{maxv}**, yielding *{len(df):,}* of the *{len(df0):,}* in total.')# ({int(len(df)/len(df0)*100)}%).')
                
            
    

class MemberGenderCard(DashComponent):
    @cached_property
    def series(self):
        return MemberDwellingsDataset().data.gender.replace({'':'(Unknown)'}).value_counts().index

    @cached_property
    def input(self):
        return dbc.Checklist(
            options=self.series,
            value=[],
            switch=True,
        )

    def layout(self,params=None):
        return dbc.Card([
            dbc.CardHeader("Filter by member gender"),
            dbc.CardBody(
                self.input,
            )
        ])


class MemberDwellingsMapCard(DashComponent):
    @cached_property
    def graph(self):
        return dcc.Graph(figure=self.plot_map())
    
    @cached_property
    def ff(self): return MemberDwellingsFigureFactory()
    
    def plot_map(self):
        return self.ff.plot_map()

    def layout(self,params=None):
        return SimpleCard(
            header=['Map of members’ apartments in Paris'],
            body=[self.graph]
        )

class Navbar(DashComponent):
    def layout(self, params=None):
        return dbc.Navbar(
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



class GeotasteLayout(DashComponent):
    def __init__(self):
        super().__init__()
        self.navbar = Navbar()
        self.member_panel_comparison = MemberPanelComparison()

    def layout(self, params=None):
        return dbc.Container([
            self.navbar.layout(params),
            self.member_panel_comparison.layout(params)
        ])

   
  
class MemberPanel(DashComponent):
    def __init__(self, title='Member Panel', **kwargs):
        super().__init__(title=title, **kwargs) 

    @cached_property
    def store(self): return dcc.Store(id=f'store__{self.name}')
    @cached_property
    def store_desc(self): return html.P('[no filter]')

    @cached_property
    def name_card(self): return MemberNameCard()
    @cached_property
    def dob_card(self): return MemberDOBCard()
    @cached_property
    def gender_card(self): return MemberGenderCard()
    
    def layout(self, params=None): 
        body = dbc.Container([
            html.H3(self.title),
            self.store_desc,
            self.name_card.layout(params),
            self.dob_card.layout(params),
            self.gender_card.layout(params),
            # self.map_dwellings_card.layout(params),
            self.store
        ])
        return body
    

    def component_callbacks(self, app):
        @app.callback(
            Output(self.store, 'data'),
            Input(self.dob_card.store, 'data'),
            State(self.store, 'data'),
        )
        def update_store_from_dob_store(new_data, current_data):
            if current_data is None: current_data = {}
            return {**current_data, **new_data}
        
        @app.callback(
            Output(self.store_desc, 'children'),
            Input(self.store, 'data'),
        )
        def update_from_store(filter_data):
            q = to_query_string(filter_data)
            if not q: q = '[no filter]'
            return [q]




class MemberPanelComparison(DashComponent):
    def __init__(self):
        super().__init__()
        self.member_panel_L = MemberPanel(name='member-panel-L')
        self.member_panel_R = MemberPanel(name='member_panel_R')

    def layout(self, params=None):
        # header = html.H2('Comparing members'),
        body = dbc.Row([
            dbc.Col(width=6, children=[self.member_panel_L.layout(params)]),
            dbc.Col(width=6, children=[self.member_panel_R.layout(params)])
        ])
        return body

### Callbacks









# @callback(
#     Output(store_member_filter, "data"),
#     [
#         Input(member_name_card.input_member, 'value'),
#         Input(input_gender, 'value'),
#         Input(graph_members_dob, 'selectedData'),
#     ],
#     State(store_member_filter, "data"),
# )
# def update_filter_from_dob(members, genders, selected_data, filter_data):
#     if filter_data is None: filter_data = {}
#     filter_data['member'] = members
#     filter_data['gender'] = genders

#     ## birth year
#     if selected_data:
#         try:
#             minx,maxx = selected_data['range']['x']
#             filter_data['birth_year'] = [(int(minx), int(maxx))]
#         except Exception as e:
#             sys.stderr.write(str(e))
#             print('!!',e)

#     return filter_data







# @callback(
#     [
#         Output(member_filter_pre, 'children'),
#         Output(map_members, 'figure'),
#     ],
#     Input(store_member_filter, "data"),
#     State(map_members, 'figure'),
# )
# def update_pre_with_query_str(filter_data, fig_old):
#     ff = FigureFactory(MemberDwellings().data)
#     q = ff.filter_query(filter_data)
#     df = ff.filter_df(q=q)
#     # pre = f'{pformat(filter_data)}\nQ: {q}'
#     pre = f'Q: {q}' if q else '[none]'
#     fig_new = plot_members_map(df)
#     fig = go.Figure(fig_new.data, go.Figure(fig_old).layout)
#     return [pre,fig]
