from typing import Any
from app_imports import *
from app_figs import *

class BaseComponent(DashComponent):
    # some will have
    figure_class = None

    ## hookups to FigureFactories
    def ff(self, filter_data={}):
        return self.figure_class(ensure_dict(filter_data))

    def plot(self, filter_data={}):
        return self.ff(ensure_dict(filter_data)).plot(**self._kwargs)
    

    ## all components can have a memory -- only activated if nec
    @cached_property
    def store(self): return dcc.Store(id=self.id('filter_data'))

    def __init__(
            self,

            # Dash arguments
            title="Dash Component", 
            name=None,
            no_store=None,
            no_attr=None,
            no_config=None,
            
            # other kwargs: color, ...
            **kwargs
            ):

        # invoke Dash component init    
        super().__init__(
            title=title, 
            name=name,
            no_store=no_store, 
            no_attr=no_attr, 
            no_config=no_config
        )

        # ensure some exist
        self.color = None
        
        # overwritten here
        for k,v in kwargs.items(): 
            setattr(self,k,v)
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





class FilterCard(BaseComponent):
    desc = 'Filter by X'
    key='relevant_col'




class FilterCard(BaseComponent):
    desc = 'Filter by X'
    key='relevant_col'

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
    def graph(self):
        return dcc.Graph(figure=self.plot())
    
    @cached_property
    def button_clear(self):
        return dbc.Button(
            "Clear", 
            color="link", 
            n_clicks=0
        )
    
    def component_callbacks(self, app):        
        @app.callback(
            Output(self.footer, 'children', allow_duplicate=True),
            Input(self.store, 'data'),
            prevent_initial_call=True
        )
        def update_filter_desc(filter_data):
            print('update_I filter_desc',filter_data)
            return dcc.Markdown(self.ff(ensure_dict(filter_data)).filter_desc)
        
        ## CLEAR?
        @app.callback(
            Output(self.store, "data", allow_duplicate=True),
            Input(self.button_clear, 'n_clicks'),
            State(self.store, 'data'),
            prevent_initial_call=True
        )
        def clear_selection(n_clicks, filter_data):
            filter_data = ensure_dict(filter_data)
            if self.key in filter_data: filter_data.pop(self.key)
            return filter_data

        @app.callback(
            Output(self.footer, 'children', allow_duplicate=True),
            Input(self.store, 'data'),
            prevent_initial_call=True
        )
        def update_filter_desc(filter_data):
            print('update_filter_desc',filter_data)
            if self.figure_class is None: raise PreventUpdate
            return dcc.Markdown(self.ff(ensure_dict(filter_data)).filter_desc)



class FilterPlotCard(FilterCard):
    def component_callbacks(self, app):

        ## CLEAR? -- OVERWRITTEN
        @app.callback(
            [
                Output(self.store, "data", allow_duplicate=True),
                Output(self.graph, "figure", allow_duplicate=True),
            ],
            Input(self.button_clear, 'n_clicks'),
            State(self.store, 'data'),
            prevent_initial_call=True
        )
        def clear_selection(n_clicks, filter_data):
            filter_data = ensure_dict(filter_data)
            if self.key in filter_data: filter_data.pop(self.key)
            return filter_data, self.plot(filter_data)

        @app.callback(
            Output(self.store, "data"),
            Input(self.graph, 'selectedData'),
            State(self.store, "data"),
        )
        def update_selection(selected_data, filter_data):
            filter_data = ensure_dict(filter_data)
            if selected_data:
                if 'range' in selected_data:
                    xrange = selected_data['range']['x']
                    print('xrange selected:',xrange)
                    minx,maxx = xrange
                    filter_data[self.key] = [(int(minx), int(maxx))]
                
                elif 'points' in selected_data:
                    active_cats = [pd['x'] for pd in selected_data['points']]
                    filter_data[self.key] = active_cats
                
            return filter_data
        
        




class MemberDOBCard(FilterPlotCard):
    desc = 'Filter by date of birth'
    key='birth_year'
    figure_class = MemberDOBFigure    
    
    
class MembershipYearCard(FilterPlotCard):
    desc = 'Filter by years of membership'
    key='membership_year'
    figure_class = MembershipYearFigure


            
    

class MemberGenderCard(FilterPlotCard):
    desc = 'Filter by gender of member'
    key='gender'
    figure_class = MemberGenderFigure

    # @cached_property
    # def series(self):
    #     return self.ff().df[self.key].value_counts().index

    # @cached_property
    # def input(self):
    #     return dbc.Checklist(
    #         options=self.series,
    #         value=[],
    #         switch=True,
    #     )

    # def layout(self,params=None):
    #     return dbc.Card([
    #         dbc.CardHeader("Filter by member gender"),
    #         dbc.CardBody([
    #             self.input,
    #             self.store,
    #         ])
    #     ])
    
    # def component_callbacks(self, app):
    #     @app.callback(
    #         Output(self.store, "data"),
    #         Input(self.input, 'value'),
    #         State(self.store, "data"),
    #     )
    #     def update_store(values, filter_data):
    #         filter_data = ensure_dict(filter_data)
    #         filter_data[self.key] = values
















class MemberDwellingsMapCard(BaseComponent):

    @cached_property
    def graph(self):
        return dcc.Graph(figure=self.plot_map())
    
    def ff(self, *args, **kwargs): return MemberDwellingsFigureFactory(*args, **kwargs)
    
    def plot_map(self):
        return self.ff().plot_map(**self._kwargs)

    def layout(self,params=None):
        return SimpleCard(
            header=['Map of members’ apartments in Paris'],
            body=[self.graph]
        )


class MemberDwellingsComparisonMapCard(MemberDwellingsMapCard):
    @cached_property
    def graph(self): return dcc.Graph()


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
        self.member_panel_L = MemberPanel(name='member_panel_L', color=LEFT_COLOR)
        self.member_panel_R = MemberPanel(name='member_panel_R', color=RIGHT_COLOR)

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
        return MemberDwellingsComparisonMapCard()
    
    def component_callbacks(self, app):
        @app.callback(
            Output(self.comparison_map_card.graph, 'figure'),
            [
                Input(self.member_panel_L.store, 'data'), 
                Input(self.member_panel_R.store, 'data')
            ],
            State(self.comparison_map_card.graph, 'figure'),
        )
        def redraw_map(filter_data_L, filter_data_R, old_figdata):
            fig_new = MemberComparisonFigureFactory(ensure_dict(filter_data_L), ensure_dict(filter_data_R)).plot_map()
            fig_old = go.Figure(old_figdata)
            fig_out = go.Figure(
                layout=fig_old.layout if fig_old.data else fig_new.layout,
                data=fig_new.data
            )
            return fig_out
        


            

        
        



   
  
class MemberPanel(BaseComponent):
    # def __init__(self, title='Member Panel', color=None, **kwargs):
    #     super().__init__(title=title, **kwargs) 
    #     self.color = color

    @cached_property
    def store(self): return dcc.Store(id=f'store__{self.name}')
    @cached_property
    def store_desc(self): return html.H3('[no filter]', style={'color':self.color, 'text-align':'center'} if self.color else {})

    @cached_property
    def name_card(self): return MemberNameCard(**self._kwargs)
    @cached_property
    def dob_card(self): return MemberDOBCard(**self._kwargs)
    @cached_property
    def membership_year_card(self): return MembershipYearCard(**self._kwargs)
    @cached_property
    def gender_card(self): return MemberGenderCard(**self._kwargs)
    @cached_property
    def map_card(self): return MemberDwellingsMapCard(**self._kwargs)
    
    def layout(self, params=None): 
        body = dbc.Container([
            self.store_desc,
            self.name_card.layout(params),
            self.dob_card.layout(params),
            self.membership_year_card.layout(params),
            self.gender_card.layout(params),
            self.map_card.layout(params),
            self.store
        ])
        return body
    

    def component_callbacks(self, app):
        @app.callback(
            Output(self.store, 'data'),
            [
                Input(self.dob_card.store, 'data'),
                Input(self.gender_card.store, 'data'),
                Input(self.membership_year_card.store, 'data'),

            ],
            State(self.store, 'data'),
        )
        def update_store_from_dob_store(new_data1, new_data2, new_data3, current_data):
            return {**ensure_dict(current_data), **ensure_dict(new_data1), **ensure_dict(new_data2), **ensure_dict(new_data3)}
        
        @app.callback(
            [
                Output(self.store_desc, 'children'),
                Output(self.map_card.graph, 'figure')
            ],
            Input(self.store, 'data'),
        )
        def datastore_updated(filter_data):
            q = to_query_string(filter_data)
            if not q: q = '[no filter]'
            # return [q]
            fig = self.map_card.ff(filter_data).plot_map(**self._kwargs)
            
            return [q, fig]














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
