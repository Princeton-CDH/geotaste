from .imports import *

BLANKSTR='‎‎‎‎'
BLANK = dcc.Markdown('\[no filter\]')
BLANKDIV = html.Div(BLANKSTR)

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
            return self.figure_class(filter_data).plot(**self._kwargs)
        else:
            return self.figure_obj.plot(**self._kwargs)
    
    

    ## all components can have a memory -- only activated if nec
    @cached_property
    def store(self): return dcc.Store(id=self.id('store'), data={})

    @cached_property
    def store_desc(self): 
        return html.Div(
            BLANKSTR, 
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
            # BLANKDIV,
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
            print(selected_data)
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
    key='membership_years'
    figure_class = MembershipYearFigure    

class MemberGenderCard(FilterPlotCard):
    desc = 'Filter by gender of member'
    key='gender'
    figure_class = MemberGenderFigure

class MemberNationalityCard(FilterPlotCard):
    desc = 'Filter by nationality of member'
    key='nationalities'
    figure_class = MemberNationalityFigure

class MemberTableCard(FilterPlotCard):
    desc = 'Filter by gender of member'
    figure_class = MemberTableFigure

    @cached_property
    def graph(self):
        return html.Div(children=[self.plot()])


class MemberMapCard(FilterPlotCard):
    desc = 'Member addresses mapped'
    # key='gender'
    figure_class = MemberMap








class MemberMapComparisonCard(MemberMapCard): pass


class MemberPanel(FilterCard):
    @cached_property
    def name_card(self): return MemberNameCard(**self._kwargs)
    @cached_property
    def dob_card(self): return MemberDOBCard(**self._kwargs)
    @cached_property
    def membership_year_card(self): return MembershipYearCard(**self._kwargs)
    @cached_property
    def gender_card(self): return MemberGenderCard(**self._kwargs)
    @cached_property
    def nation_card(self): return MemberNationalityCard(**self._kwargs)
    @cached_property
    def map_card(self): return MemberMapCard(**self._kwargs)
    @cached_property
    def table_card(self): return MemberTableCard(**self._kwargs)
    
    def layout(self, params=None): 
        body = dbc.Container([
            html.Div(self.store_desc, style={'text-align':'center'}),
            self.name_card.layout(params),
            self.membership_year_card.layout(params),
            self.dob_card.layout(params),
            self.gender_card.layout(params),
            self.nation_card.layout(params),
            self.map_card.layout(params),
            self.table_card.layout(params),
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
                Input(self.nation_card.store, 'data'),
                Input(self.map_card.store, 'data'),
                # Input(self.table_card.store, 'data'),
            ]
        )
        def component_filters_updated(*filters_d):
            return intersect_filters(*filters_d)
        
        @app.callback(
            [
                Output(self.membership_year_card.graph, 'figure'),
                Output(self.dob_card.graph, 'figure'),
                Output(self.gender_card.graph, 'figure'),
                Output(self.nation_card.graph, 'figure'),
                Output(self.table_card.graph, 'children'),
                Output(self.map_card.graph, 'figure'),
            ],
            Input(self.store, 'data'),
            State(self.map_card.graph, 'figure'),
        )
        def datastore_updated(panel_data, map_figdata):
            filtered_keys = set(panel_data.get('intension',{}).keys())
            print('filtered_keys',filtered_keys)
            
            cards = [self.membership_year_card, self.dob_card, self.gender_card, self.nation_card, self.table_card, self.map_card]
            out = [
                (dash.no_update if card.key in filtered_keys else card.plot(panel_data))
                for card in cards
            ]
            if out[-1]!=dash.no_update:
                new_fig = out[-1]
                old_fig = go.Figure(map_figdata)
                out_fig = go.Figure(data=new_fig.data, layout=old_fig.layout)
                out[-1] = out_fig
            return out

            

            # # membership year
            # out.append(
            #     dash.no_update 
            #     if self.membership_year_card.key in filtered_keys 
            #     else self.membership_year_card.plot(panel_data)
            # )
            
            # out.append(
            #     dash.no_update 
            #     if self.dob_card.key in filtered_keys 
            #     else self.dob_card.plot(panel_data)
            # )

            # out.append(
            #     dash.no_update 
            #     if self.gender_card.key in filtered_keys 
            #     else self.gender_card.plot(panel_data)
            # )

            # old_fig = go.Figure(map_figdata)
            # new_fig = self.map_card.plot(panel_data)
            # out_fig = go.Figure(data=new_fig.data, layout=old_fig.layout)
            # out.append(out_fig)


            # return out







# class MemberDwellingsMapCard(FilterComponent):

#     @cached_property
#     def graph(self):
#         return dcc.Graph(figure=self.plot_map())
    
#     def ff(self, *args, **kwargs): return MemberDwellingsFigureFactory(*args, **kwargs)
    
#     def plot_map(self):
#         return self.ff().plot_map(**self._kwargs)

#     def layout(self,params=None):
#         return SimpleCard(
#             header=['Map of members’ apartments in Paris'],
#             body=[self.graph]
#         )


# class MemberDwellingsComparisonMapCard(MemberDwellingsMapCard):
#     @cached_property
#     def graph(self): return dcc.Graph()

        
        