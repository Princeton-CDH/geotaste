from typing import Any
from app_imports import *
from app_figs import *


class BaseComponent(DashComponent):
    def __init__(self, title="Dash", name=None,
                 no_store=None, no_attr=None, no_config=None,
                 **kwargs):
        super().__init__(title=title, name=name,
                 no_store=no_store, no_attr=no_attr, no_config=no_config)
        for k,v in kwargs.items(): setattr(self,k,v)
        self._kwargs = kwargs



class SimpleCard(dbc.Card):
    def __init__(self, body=[], header=[], footer=[], **kwargs):
        children = []
        if header: children+=[dbc.CardHeader(header)]
        if body: children+=[dbc.CardBody(body)]
        if footer: children+=[dbc.CardFooter(footer)]
        super().__init__(children, outline=True, **kwargs)




class MemberNameCard(BaseComponent):
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









class MemberDOBCard(BaseComponent):
    desc = 'Filter by date of birth'


    @cached_property
    def store(self): return dcc.Store(id=f'store__{self.name}')

    @cached_property
    def header(self):
        return dbc.CardHeader(
            dbc.Row([
                dbc.Col(self.desc),
                dbc.Col(self.button_clear, style={'text-align':'right'})
            ])
        )
    
    @cached_property
    def body(self):
        return dbc.CardBody([
            self.graph,
            self.store,
        ])
    
    @cached_property
    def footer(self):
        return dbc.CardFooter()


    def layout(self, params=None):
        return dbc.Card([
            self.header, 
            self.body,
            self.footer,
        ])
    
    @cached_property
    def filter_desc(self): return html.Span()

    @cached_property
    def graph(self):
        return dcc.Graph(figure=self.plot())
    
    def ff(self, filter_data={}):
        return MemberFigureFactory(filter_data)

    def plot(self, filter_data={}, ff=None):
        return self.ff(filter_data).plot_dob(**self._kwargs)

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
            print('GOT:',selected_data)
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
        
        # @app.callback(
        #     Output(self.footer, 'children', allow_duplicate=True),
        #     Input(self.store, 'data'),
        #     prevent_initial_call=True
        # )
        # def update_filter_desc(filter_data, key='birth_year'):
        #     df0 = self.ff().df
        #     df = self.ff(filter_data).df
        #     res = filter_data.get(key)
        #     minv,maxv = df0[key].dropna().apply(int).min(), df0[key].dropna().apply(int).max()
        #     o = ''            
        #     if res:
        #         obj = res[0]
        #         if len(obj)==2:
        #             minv,maxv = obj
        #     o = dcc.Markdown(f'*Filtering members born between **{minv}** and **{maxv}** yields *{len(df):,}* of *{len(df0):,}* members of the library.*')
        #     return o

                
            
    

class MemberGenderCard(BaseComponent):
    @cached_property
    def store(self): return dcc.Store(id=f'store__{self.name}')
    
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
            dbc.CardBody([
                self.input,
                self.store,
            ])
        ])
    
    def component_callbacks(self, app):
        @app.callback(
            Output(self.store, "data"),
            Input(self.input, 'value'),
        )
        def update_store(values):
            print(values)
            return {'gender':values}


class MemberDwellingsMapCard(BaseComponent):

    @cached_property
    def graph(self):
        return dcc.Graph()#figure=self.plot_map())
    
    @cached_property
    def ff(self): return MemberDwellingsFigureFactory()
    
    def plot_map(self):
        return self.ff.plot_map(**self._kwargs)

    def layout(self,params=None):
        return SimpleCard(
            header=['Map of members’ apartments in Paris'],
            body=[self.graph]
        )

class Navbar(BaseComponent):
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



class GeotasteLayout(BaseComponent):
    def __init__(self):
        super().__init__()
        self.navbar = Navbar()
        self.member_panel_comparison = MemberPanelComparison()

    def layout(self, params=None):
        return dbc.Container([
            self.navbar.layout(params),
            dbc.Container(
                self.member_panel_comparison.layout(params),
                className='content-container'
            )
        ], className='layout-container')

class MemberPanelComparison(BaseComponent):
    def __init__(self):
        super().__init__()
        self.navbar = Navbar()
        self.member_panel_L = MemberPanel(name='member_panel_L', color='#7d6ab6')
        self.member_panel_R = MemberPanel(name='member_panel_R', color='#1a6b47')

    def layout(self, params=None):
        return dbc.Container([
            dbc.Row([
                dbc.Col(
                    self.member_panel_L.layout(params),
                    width=6
                ),
                dbc.Col(
                    self.member_panel_R.layout(params),
                    width=6
                ),
            ]),
            
            dbc.Row(
                dbc.Col(
                    self.comparison_map_card.layout(params),
                    width=12,
                    className='comparison_map_card_col'
                )
            )
        ])
    
    @cached_property
    def comparison_map_card(self):
        return MemberDwellingsMapCard()
    
    def component_callbacks(self, app):
        @app.callback(
            Output(self.comparison_map_card.graph, 'figure'),
            [Input(self.member_panel_L.store, 'data'), Input(self.member_panel_R.store, 'data')]
        )
        def redraw_map(filter_data_L, filter_data_R):
            dfL = MemberDwellingsFigureFactory(filter_data_L).df
            dfR = MemberDwellingsFigureFactory(filter_data_R).df

            df = pd.concat([dfL.assign(color='red'), dfR.assign(color='blue')])
            ff = MemberDwellingsFigureFactory(df=df)
            return ff.plot_map()
        
        



   
  
class MemberPanel(BaseComponent):
    # def __init__(self, title='Member Panel', color=None, **kwargs):
    #     super().__init__(title=title, **kwargs) 
    #     self.color = color

    @cached_property
    def store(self): return dcc.Store(id=f'store__{self.name}')
    @cached_property
    def store_desc(self): return html.P('[no filter]')

    @cached_property
    def name_card(self): return MemberNameCard(**self._kwargs)
    @cached_property
    def dob_card(self): return MemberDOBCard(**self._kwargs)
    @cached_property
    def gender_card(self): return MemberGenderCard(**self._kwargs)
    @cached_property
    def map_dwellings_card(self): return MemberDwellingsMapCard(**self._kwargs)
    
    def layout(self, params=None): 
        body = dbc.Container([
            html.H3(self.title),
            self.store_desc,
            self.name_card.layout(params),
            self.dob_card.layout(params),
            self.gender_card.layout(params),
            self.map_dwellings_card.layout(params),
            self.store
        ])
        return body
    

    def component_callbacks(self, app):
        @app.callback(
            Output(self.store, 'data'),
            [
                Input(self.dob_card.store, 'data'),
                Input(self.gender_card.store, 'data'),
            ],
            State(self.store, 'data'),
        )
        def update_store_from_dob_store(new_data1, new_data2, current_data):
            if current_data is None: current_data = {}
            return {**current_data, **new_data1, **new_data2}
        
        @app.callback(
            [
                Output(self.store_desc, 'children'),
                Output(self.map_dwellings_card.graph, 'figure')
            ],
            Input(self.store, 'data'),
        )
        def datastore_updated(filter_data):
            q = to_query_string(filter_data)
            if not q: q = '[no filter]'
            
            ff = MemberDwellingsFigureFactory(filter_data)
            fig = ff.plot_map(**self._kwargs)
            
            return [q, fig]




class MemberPanelComparisonByRow(BaseComponent):
    def __init__(self):
        super().__init__()
        self.left = MemberPanel(name='member-panel-L')
        self.right = MemberPanel(name='member_panel_R')

    @cached_property
    def name_card(self):
        return MemberPanelComparisonRow(
            self.left,
            self.right,
            'name_card',
            'Filter by member name'
        )
    
    @cached_property
    def dob_card(self):
        return MemberPanelComparisonRow(
            self.left,
            self.right,
            'dob_card',
            'Filter by date of birth'
        )
    
    @cached_property
    def gender_card(self):
        return MemberPanelComparisonRow(
            self.left,
            self.right,
            'gender_card',
            'Filter by member gender'
        )
    
    def layout(self, params=None):
        return dbc.Container([
            self.name_card.layout(params),
            self.dob_card.layout(params),
            self.gender_card.layout(params),
        ])



class MemberPanelComparisonRow(BaseComponent):
    def __init__(self, left_panel, right_panel, widget_name, header=[], footer=[]):
        super().__init__()
        self.left_widget = getattr(left_panel, widget_name)
        self.right_widget = getattr(right_panel, widget_name)
        self.header = header
        self.footer = footer

    def layout(self, params=None):
        return SimpleCard(
            header=self.header,
            body=dbc.Row([
                dbc.Col(self.left_widget.layout(params), width=6),
                dbc.Col(self.right_widget.layout(params), width=6),
            ])
        )



### Callbacks



class MemberDOBComparison(BaseComponent):
    def __init__(self, left_panel, right_panel, widget_name, header=[], footer=[]):
        super().__init__()
        self.left_widget = getattr(left_panel, widget_name)
        self.right_widget = getattr(right_panel, widget_name)
        self.header = header
        self.footer = footer

    def layout(self, params=None):
        return SimpleCard(
            header=self.header,
            body=dbc.Row([
                dbc.Col(self.left_widget.layout(params), width=6),
                dbc.Col(self.right_widget.layout(params), width=6),
            ])
        )    

