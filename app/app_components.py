from app_imports import *

BLANKSTR='‎‎‎‎'
BLANK = dcc.Markdown('\[no filter\]')

class BaseComponent(DashComponent):
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


class FilterComponent(BaseComponent):
    desc = 'Filter by X'
    key='relevant_col'
    records_name='members'
    
    # some will have
    figure_class = None

    @cached_property
    def figure_obj(self): return self.figure_class()
    def plot(self, filter_data={}): 
        if filter_data:
            return self.ff(filter_data).plot(**self._kwargs)
        else:
            return self.figure_obj.plot(**self._kwargs)
    
    

    ## all components can have a memory -- only activated if nec
    @cached_property
    def store(self): return dcc.Store(id=self.id('store'), data={})

    @cached_property
    def store_desc(self): 
        return html.Div(
            '[no filter]', 
            style={
                'color':self.color if self.color else 'inherit', 
                # 'text-align':'center'
            }
        )




class FilterCard(FilterComponent):

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
            BLANK,
            self.graph,
            self.store
        ])
    
    @cached_property
    def footer(self):
        return dbc.CardFooter(self.store_desc)


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
            Output(self.store_desc, 'children'),
            Input(self.store, 'data'),
            prevent_initial_call=True
        )
        def store_data_updated(store_data):
            print('store_data_updated',store_data)
            res=describe_filters(store_data, records_name=self.records_name)
            return dcc.Markdown(res) if res else BLANK
        
        # ## CLEAR?
        # @app.callback(
        #     Output(self.store, "data", allow_duplicate=True),
        #     Input(self.button_clear, 'n_clicks'),
        #     prevent_initial_call=True
        # )
        # def clear_selection(n_clicks):
        #     return {}



class FilterPlotCard(FilterCard):
    def component_callbacks(self, app):
        # do my parent's too
        super().component_callbacks(app)

        # ## CLEAR? -- OVERWRITTEN
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
            Output(self.store, "data"),
            Input(self.graph, 'selectedData'),
            prevent_initial_call=True
        )
        def graph_selection_updated(selected_data):
            return self.figure_obj.selected(selected_data)
        
        



















class MemberNameCard(FilterCard):
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












class MemberPanel(FilterCard):
    # def __init__(self, title='Member Panel', color=None, **kwargs):
    #     super().__init__(title=title, **kwargs) 
    #     self.color = color

    # @cached_property
    # def store_desc(self): return html.H3('[no filter]', style={'color':self.color, 'text-align':'center'} if self.color else {})

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
            html.Div(self.store_desc, style={'text-align':'center'}),
            self.name_card.layout(params),
            self.membership_year_card.layout(params),
            self.dob_card.layout(params),
            self.gender_card.layout(params),
            self.map_card.layout(params),
            self.store
        ])
        return body
    

    def component_callbacks(self, app):
        super().component_callbacks(app)

        @app.callback(
            Output(self.store, 'data'),
            [
                Input(self.membership_year_card.store, 'data'),
                Input(self.dob_card.store, 'data'),
                Input(self.gender_card.store, 'data'),
            ]
        )
        def component_filters_updated(*filters_d):
            return intersect_filters(*filters_d)
        
        @app.callback(
            Output(self.map_card.graph, 'figure'),
            Input(self.store, 'data'),
        )
        def datastore_updated(store_data):
            return MemberMap(store_data).plot(**self._kwargs)







class MemberDwellingsMapCard(FilterComponent):

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

        
        