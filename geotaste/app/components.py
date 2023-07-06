from ..imports import *

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
        self.filter_data = {}
        
        # overwritten here
        for k,v in kwargs.items(): 
            setattr(self,k,v)
        self._kwargs = kwargs

    

class FilterComponent(BaseComponent):
    desc = 'Filter by X'
    key='relevant_col'
    records_name='members'
    
    # some will have
    figure_factory = None
    dataset_class = None

    @property
    def ff(self): 
        if self.figure_factory is not None:
            return self._ff(serialize_d(self.filter_data))
    @cache
    def _ff(self, filter_data=None):
        if self.figure_factory is not None:
            filter_data = unserialize_d(filter_data) if filter_data is not None else {}
            return self.figure_factory(self.filter_data)
    
    @cached_property
    def dataset(self): 
        if self.dataset_class is not None:
            return self.dataset_class()

    def plot(self, filter_data={}, existing_fig=None): 
        # filter
        if filter_data:
            fig = self.figure_factory(filter_data).plot(**self._kwargs)
        else:
            fig = self.ff.plot(**self._kwargs)

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
        return dcc.Store(id=self.id(self.name), data={})
        # return dcc.Store(id=self.id(f'store-{self.__class__.__name__}'), data={})
    
    @property
    def filter_desc(self):
        # return describe_filters(self.filter_data)
        return format_intension(self.filter_data.get(INTENSION_KEY,{}))
    
    @property
    def filter_key(self):
        return self.filter_desc


    @cached_property
    def store_desc(self): return html.Span(NOFILTER, className='store_desc')


class FilterCard(FilterComponent):
    def layout(self, params=None, header=True, body=True, footer=True, **kwargs):
        children = []
        if header: children.append(self.header)
        if body: children.append(self.body)
        if footer: children.append(self.footer)
        return dbc.Card(children, **kwargs)


    @cached_property
    def header(self):
        return dbc.CardHeader(
            [
                html.Div(self.button_showhide, className='button_showhide_div'),
                html.P(self.desc),
            ]
        )
    
    @cached_property
    def body(self):
        return dbc.Collapse(dbc.CardBody(self.content), is_open=True)
    
    
    ## SUBCLASS
    @cached_property
    def content(self): 
        # subclass!
        return ''
        
    @cached_property
    def footer(self):
        style_d={'color':self.color if self.color else 'inherit'}
        return dbc.Collapse(
            dbc.CardFooter(
                [
                    self.store,
                    html.Div(self.button_clear, className='button_clear_div'),
                    html.Div(self.store_desc, className='card-footer-desc')
                ],
                style=style_d
            ),
            is_open=False
        )
    
    @cached_property
    def store_desc(self): 
        return dbc.Button(
            '', 
            className='store_desc', 
            color='link',
            id=self.id('store_desc')
        )

    @cached_property
    def button_clear(self):
        return dbc.Button(
            "[x]", 
            color="link", 
            n_clicks=0,
            className='button_clear',
            id=self.id('button_clear')
        )
    
    @cached_property
    def button_showhide(self):
        return dbc.Button(
            "[-]", 
            color="link", 
            n_clicks=0,
            className='button_showhide'
        )
    
    def component_callbacks(self, app):        
        @app.callback(
            [
                Output(self.store_desc, 'children', allow_duplicate=True),
                Output(self.body, 'is_open', allow_duplicate=True),
                Output(self.footer, 'is_open', allow_duplicate=True)
            ],
            Input(self.store, 'data'),
            [
                State(self.body, 'is_open'),
                State(self.footer, 'is_open')
            ],
            prevent_initial_call=True
        )
        def store_data_updated(store_data, body_open, footer_open):
            # filter cleared?
            if not store_data:
                return BLANK,body_open,footer_open
            else:
                print(f'[{nowstr()}] store_data_updated: {self.__class__.__name__} ({self.name})')
                res=describe_filters(store_data, records_name=self.records_name)
                o1 = dcc.Markdown(res) if res else BLANK
                return (o1,True,True)
        


        ## buttons

        @app.callback(
            Output(self.body, "is_open", allow_duplicate=True),
            Input(self.button_showhide, "n_clicks"),
            State(self.body, "is_open"),
            prevent_initial_call=True
        )
        def toggle_collapse(n, is_open):
            if n: return not is_open
            return is_open
        

        # MUST BE SUBCLASSED??
        # @app.callback(
        #     [
        #         Output(self.store, "data", allow_duplicate=True),
        #         Output(self.footer, "is_open", allow_duplicate=True),
        #     ],
        #     Input(self.button_clear, 'n_clicks'),
        #     prevent_initial_call=True
        # )
        # def clear_selection(n_clicks):
        #     return {}, False
    
        





class FilterPlotCard(FilterCard):
    @cached_property
    def content(self): return self.graph
    @cached_property
    def graph(self): return dcc.Graph(figure=self.plot())

    def component_callbacks(self, app):
        # do my parent's too
        super().component_callbacks(app)

        @app.callback(
            [
                Output(self.store, "data", allow_duplicate=True),
                Output(self.footer, "is_open", allow_duplicate=True),
                Output(self.graph, "figure", allow_duplicate=True),
            ],
            Input(self.button_clear, 'n_clicks'),
            prevent_initial_call=True
        )
        def clear_selection(n_clicks):
            return {}, False, self.plot()

        @app.callback(
            Output(self.store, "data", allow_duplicate=True),
            Input(self.graph, 'selectedData'),
            prevent_initial_call=True
        )
        def graph_selection_updated(selected_data):
            print('graph_selection_updated')
            return self.ff.selected(selected_data)
        
        















class FilterInputCard(FilterCard):
    desc = 'Filter by input'
    key=''
    
    @cached_property
    def content(self):  return self.input
    @cached_property
    def input(self):
        return dcc.Dropdown()
    
    def component_callbacks(self, app):
        # do my parent's too
        super().component_callbacks(app)

        # # ## CLEAR? -- OVERWRITTEN
        # @app.callback(
        #     [
        #         Output(self.store, "data", allow_duplicate=True),
        #         Output(self.input, "value", allow_duplicate=True),
        #     ],
        #     Input(self.button_clear, 'n_clicks'),
        #     prevent_initial_call=True
        # )
        # def clear_selection(n_clicks):
        #     print('clear_selection')
        #     return {}, []

        # @app.callback(
        #     Output(self.store, "data", allow_duplicate=True),
        #     Input(self.input, 'value'),
        #     prevent_initial_call=True
        # )
        # def input_value_changed(vals):
        #     if not vals: raise PreventUpdate
        #     if self.dataset_obj is not None:
        #         return self.dataset_obj.filter_series(
        #             self.key,
        #             vals=vals
        #         )
        #     return {}
    



class FilterTableCard(FilterPlotCard):
    @cached_property
    def table(self): return html.Div(children=[self.plot()])
    
    
    @cached_property
    def content(self): return self.table

    def component_callbacks(self, app):
        pass


