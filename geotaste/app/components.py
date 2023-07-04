from ..imports import *

BLANKSTR='‎‎‎‎'
BLANK = '(unfiltered)'
BLANKDIV = html.Div(BLANKSTR)
NOFILTER = BLANK

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
        self.filter_data = {}
        
        # overwritten here
        for k,v in kwargs.items(): 
            setattr(self,k,v)
        self._kwargs = kwargs

    ## all components can have a memory -- only activated if nec
    @cached_property
    def store(self):
        return dcc.Store(id=self.id('store-'+self.__class__.__name__), data={})


class FilterComponent(BaseComponent):
    desc = 'Filter by X'
    key='relevant_col'
    records_name='members'
    
    # some will have
    figure_class = None
    dataset_class = None

    @cached_property
    def figure_obj(self): return self.figure_class() if self.figure_class is not None else None

    @cached_property
    def dataset_obj(self): return self.dataset_class() if self.dataset_class is not None else None

    def plot(self, filter_data={}, existing_fig=None): 
        # filter
        if filter_data:
            fig = self.figure_class(filter_data).plot(**self._kwargs)
        else:
            fig = self.figure_obj.plot(**self._kwargs)

        # retain layout
        if existing_fig is not None:
            old_fig = go.Figure(existing_fig) if type(existing_fig)!=go.Figure else existing_fig
            out_fig = go.Figure(data=fig.data, layout=old_fig.layout)
        else:
            out_fig = fig

        # return
        return out_fig
    
    

    ## all components can have a memory -- only activated if nec
    @cached_property
    def store(self):
        return dcc.Store(id=self.id('store-'+self.__class__.__name__), data={})

    @cached_property
    def store_desc(self): return html.Span(NOFILTER, className='store_desc')

    def component_callbacks(self, app):        
        @app.callback(
            Output(self.store_desc, 'children'),
            Input(self.store, 'data'),
            prevent_initial_call=True
        )
        def store_data_updated(store_data):
            print('store_data_updated')
            res=describe_filters(store_data, records_name=self.records_name)
            return dcc.Markdown(res) if res else BLANK


class FilterCard(FilterComponent):

    @cached_property
    def header_with_clear(self):
        return dbc.CardHeader(
            dbc.Row([
                dbc.Col(self.desc),
                dbc.Col(self.button_clear, style={'textAlign':'right'})
            ], className='pl0 pr0 card_header_row')
        )
    
    @cached_property
    def header(self):
        return dbc.CardHeader(self.desc)
    
    @cached_property
    def body(self):
        return dbc.CardBody([self.graph])
    
    def layout(self, params=None, header=True, body=True, footer=True, **kwargs):
        children = []
        if header: children.append(self.header)
        if body: children.append(self.body)
        if footer: children.append(self.footer)
        return dbc.Card(children, **kwargs)
    
    @cached_property
    def footer(self):
        return dbc.CardFooter(
            [
                self.store, 
                html.Div(self.button_clear, style={'float':'right'}),
                html.Div(self.store_desc, style={'float':'left'}),
            ],
            style={
                'color':self.color if self.color else 'inherit', 
            }
        )

    @cached_property
    def graph(self):
        return dcc.Graph(figure=self.plot())
    
    @cached_property
    def store_desc(self): return dbc.Button(NOFILTER, className='store_desc', color='link')

    @cached_property
    def button_clear(self):
        return dbc.Button(
            "[reset]", 
            color="link", 
            n_clicks=0,
            className='button_clear'
        )
    
    
        





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
            print('clear_selection')
            return {}, self.plot()

        @app.callback(
            Output(self.store, "data"),
            Input(self.graph, 'selectedData'),
            prevent_initial_call=True
        )
        def graph_selection_updated(selected_data):
            print('graph_selection_updated')
            return self.figure_obj.selected(selected_data)
        
        















class FilterInputCard(FilterCard):
    desc = 'Filter by input'
    key=''
    
    @cached_property
    def body(self):
        return dbc.CardBody([self.input])
    
    @cached_property
    def input(self):
        return dcc.Dropdown()
    
    def component_callbacks(self, app):
        # do my parent's too
        super().component_callbacks(app)

        # ## CLEAR? -- OVERWRITTEN
        @app.callback(
            [
                Output(self.store, "data", allow_duplicate=True),
                Output(self.input, "value", allow_duplicate=True),
            ],
            Input(self.button_clear, 'n_clicks'),
            prevent_initial_call=True
        )
        def clear_selection(n_clicks):
            print('clear_selection')
            return {}, []

        @app.callback(
            Output(self.store, "data"),
            Input(self.input, 'value'),
            prevent_initial_call=True
        )
        def input_value_changed(vals):
            if not vals: raise PreventUpdate
            if self.dataset_obj is not None:
                return self.dataset_obj.filter_series(
                    self.key,
                    vals=vals
                )
            return {}
    



class FilterTableCard(FilterPlotCard):
    @cached_property
    def table(self): return html.Div(children=[self.plot()])
    
    @cached_property
    def body(self): return dbc.CardBody([self.table])

    def component_callbacks(self, app):
        pass


