from .imports import *


class BaseComponent(DashComponent, Logmaker):
    def __init__(
            self,

            # Dash arguments
            title="Dash Component", 
            name=None,
            no_store=None,
            no_attr=None,
            no_config=None,

            # other kwargs: color, ...
            name_prefix=None,
            **kwargs
            ):

        # invoke Dash component init    
        name=name if name else self.__class__.__name__
        if name_prefix: name=f'{name_prefix}-{name}'
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

    @cached_property
    def subcomponents(self):
        return []  # subclass this
    @cached_property
    def graph_subcomponents(self):
        return [
            card for card in self.subcomponents
            if hasattr(card,'graph')
        ]
    
    @cached_property
    def content(self,params=None):
        cards=[
            card.layout(params)
            for card in self.subcomponents
        ]
        return dbc.Container(cards if cards else BLANK)
    
    def layout(self, params=None): return self.content
    

    




class CollapsibleCard(BaseComponent):
    def layout(self, params=None, header=True, body=True, footer=True, **kwargs):
        children = []
        if header and self.header is not None: children.append(self.header)
        if body and self.body is not None: children.append(self.body)
        if footer and self.footer is not None: children.append(self.footer)
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
        logger.debug(f'creating body for {self.name}')
        return dbc.Collapse(
            dbc.CardBody(self.content), 
            is_open=True, 
            id=self.id('body')
        )
    
    @cached_property
    def footer(self):
        return dbc.Collapse(
            dbc.CardFooter(BLANK), 
            is_open=False,
            id=self.id('footer')
        )
    
    
    @cached_property
    def button_showhide(self):
        return dbc.Button(
            "[-]", 
            color="link", 
            n_clicks=0,
            className='button_showhide',
            id=self.id('button_showhide')
        )
    
    def component_callbacks(self, app):        
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

    

class FigureComponent(BaseComponent):
    figure_factory = None
    key='relevant_col'
    records_name='members'

    def ff(self, filter_data={}): 
        if self.figure_factory is not None:
            return self.figure_factory({**self.filter_data, **filter_data})
        
    def plot(self, filter_data={}, existing_fig=None, **kwargs):
        fig = self.ff(filter_data).plot(**{**self._kwargs, **kwargs})
        if existing_fig: fig = combine_figs(fig, existing_fig)
        return fig

    @cached_property
    def series(self): return self.ff().series

    def unique(self, **kwargs): return self.ff().unique(**kwargs)



        
class FilterComponent(FigureComponent):
    desc = 'Filter by X'
    
    @cached_property
    def store(self):
        return dcc.Store(id=self.id(self.name), data={})

    @property
    def filter_desc(self):
        return format_intension(self.filter_data.get(INTENSION_KEY,{}))
    
    @property
    def filter_key(self): return self.filter_desc

    @cached_property
    def store_desc(self): 
        return html.Span(UNFILTERED, className='store_desc')

    def intersect_filters(self, *filters_d):
        logger.debug(f'intersecting {len(filters_d)} filters')
        return intersect_filters(*filters_d)
    










class FilterCard(FilterComponent, CollapsibleCard):
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
            is_open=False,
            id=self.id('footer')
        )
    
    @cached_property
    def store_desc(self): 
        return dbc.Button(
            UNFILTERED, 
            className='store_desc', 
            color='link',
            id=self.id(f'store_desc')
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
    
    def component_callbacks(self, app):
        super().component_callbacks(app)

        @app.callback(
            [
                Output(self.store_desc, 'children', allow_duplicate=True),
                Output(self.footer, 'is_open', allow_duplicate=True)
            ],
            Input(self.store, 'data'),
            prevent_initial_call=True
        )
        def store_data_updated(store_data):
            # filter cleared?
            if not store_data:
                return UNFILTERED, False

            logger.debug('store_data_updated')
            res=describe_filters(store_data, records_name=self.records_name)
            o1 = dcc.Markdown(res) if res else UNFILTERED
            return o1, True

    










class FilterPlotCard(FilterCard):
    @cached_property
    def content(self): return self.graph
    @cached_property
    def graph(self): 
        return dcc.Graph(
            figure=go.Figure(), #self.plot(),
            id=self.id('graph')
        )

    def component_callbacks(self, app):
        # do my parent's too
        super().component_callbacks(app)

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
            Output(self.store, "data", allow_duplicate=True),
            Input(self.graph, 'selectedData'),
            prevent_initial_call=True
        )
        def graph_selection_updated(selected_data):
            logger.debug('graph_selection_updated')
            return self.ff().selected(selected_data)
        
        

















class FilterInputCard(FilterCard):
    desc = 'Filter by input'
    key=''
    placeholder = 'Select'
    multi = True
    sort_by_count = True
    
    @cached_property
    def content(self): return self.input
    @cached_property
    def input(self):
        l=self.unique(sort_by_count=self.sort_by_count)
        return dcc.Dropdown(
            options = [dict(value=lbl, label=lbl)  for lbl in l],
            value = [] if self.multi else '',
            multi=self.multi,
            placeholder=self.placeholder,
            id=self.id('input')
        )


    
    
    
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
            logger.debug('clear_selection')
            return {}, []

        @app.callback(
            Output(self.store, "data", allow_duplicate=True),
            Input(self.input, 'value'),
            prevent_initial_call=True
        )
        def input_value_changed(vals):
            if not vals: raise PreventUpdate
            if self.dataset is not None:
                return self.dataset.filter_series(
                    self.key,
                    vals=vals
                )
            return {}
    






class MemberNameCard(FilterInputCard):
    desc = 'Filter by member name'
    key='member_name'
    placeholder='Select individual members'
    figure_factory = MemberNameFigure

class MemberDOBCard(FilterPlotCard):
    desc = 'Filter by date of birth'
    key='member_birth_year'
    figure_factory = MemberDOBFigure    
    
class MembershipYearCard(FilterPlotCard):
    desc = 'Filter by years of membership'
    key='member_membership_years'
    figure_factory = MembershipYearFigure    

class MemberGenderCard(FilterPlotCard):
    desc = 'Filter by gender of member'
    key='member_gender'
    figure_factory = MemberGenderFigure

class MemberNationalityCard(FilterPlotCard):
    desc = 'Filter by nationality of member'
    key='member_nationalities'
    figure_factory = MemberNationalityFigure

    @cached_property
    def graph(self):
        return dcc.Graph(figure=self.plot(), config={'displayModeBar':False})

class MemberArrondCard(FilterPlotCard):
    desc = 'Filter by arrondissement'
    key='arrond_id'
    figure_factory = MemberArrondMap






class BookTitleCard(FilterInputCard):
    desc = 'Filter by book title'
    key='book_title'
    multi = True
    placeholder = 'Select books by title'
    figure_factory = BookTitleFigure


class CreatorNameCard(FilterInputCard):
    desc = 'Filter by creator'
    key='creator_name'
    placeholder = 'Select books by creator'
    figure_factory = CreatorNameFigure
    

class BookYearCard(FilterPlotCard):
    desc = "Date of book's publication"
    key='year'
    figure_factory = BookYearFigure

class CreatorGenderCard(FilterPlotCard):
    desc = 'Filter by gender of creator'
    key='creator_Gender'
    figure_factory = CreatorGenderFigure





