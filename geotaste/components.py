from .imports import *


class BaseComponent(DashComponent, Logmaker):
    name = None

    def __init__(
            self,

            # Dash arguments
            title="Dash Component", 
            name=None,
            no_store=None,
            no_attr=None,
            no_config=None,

            # other kwargs: color, ...
            name_context=None,
            name_add_uuid=False,
            **kwargs
            ):

        # invoke Dash component init    
        name=name if name else (self.name if self.name else self.__class__.__name__)
        if name_context and name_context!=name: name=f'{name}-{name_context}'
        if name_add_uuid: name = name.split('_',1)[0] + '_' + uid(4)

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
    def store_subcomponents(self):
        return [
            card for card in self.subcomponents
            if hasattr(card,'store')
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
    body_is_open = False

    def layout(self, params=None, header=True, body=True, footer=True, **kwargs):
        logger.trace(self.name)
        children = []
        if header and self.header is not None: children.append(self.header)
        if body and self.body is not None: children.append(self.body)
        if footer and self.footer is not None: children.append(self.footer)
        return dbc.Card(children, **kwargs)

    @cached_property
    def header(self):
        logger.trace(self.name)
        return dbc.CardHeader(
            [
                html.Div(self.button_showhide, className='button_showhide_div'),
                html.P(self.desc),
            ]
        )
    
    @cached_property
    def body(self):
        logger.trace(self.name)
        return dbc.Collapse(
            dbc.CardBody(self.content), 
            is_open=self.body_is_open, 
            id=self.id('body')
        )
    
    @cached_property
    def footer(self):
        logger.trace(self.name)
        return dbc.Collapse(
            dbc.CardFooter(BLANK), 
            is_open=False,
            id=self.id('footer')
        )
    
    
    @cached_property
    def button_showhide(self):
        logger.trace(self.name)
        return dbc.Button(
            "[-]", 
            color="link", 
            n_clicks=0,
            className='button_showhide',
            id=self.id('button_showhide')
        )
    
    def component_callbacks(self, app):       
        logger.trace(self.name) 
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


# @cache
@cache_obj.memoize()
def plot_cache(figure_class, serialized_data):
    logger.debug(f'plot_cache({figure_class.__name__}, {serialized_data})')
    filter_data,existing_fig,kwargs = (
        unserialize(serialized_data) 
        if serialized_data 
        else ({},None,{})
    )
    ff = figure_class(filter_data)
    fig = ff.plot(**kwargs)
    if existing_fig: 
        fig = combine_figs(fig, existing_fig)
    return fig

class FigureComponent(BaseComponent):
    figure_factory = None
    records_name='members'

    def ff(self, filter_data={}): 
        if self.figure_factory is not None:
            return self.figure_factory(filter_data)
        
    def plot(self, filter_data={}, existing_fig=None, **kwargs):
        kwargs = {**self._kwargs, **kwargs}
        serialized_data = serialize([filter_data, existing_fig, kwargs])
        return plot_cache(
            self.figure_factory, 
            serialized_data
        )

        

    @cached_property
    def series(self): return self.ff().series
    @cached_property
    def key(self): return self.ff().key

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
        filters_d = [d for d in filters_d if d]
        return {k:v for d in filters_d for k,v in d.items()}
    










class FilterCard(FilterComponent, CollapsibleCard):
    @cached_property
    def footer(self):
        logger.trace(self.name)
        style_d={'color':self.color if self.color else 'inherit'}
        return dbc.Collapse(
            dbc.CardFooter(dbc.Row(
                [
                    dbc.Col(
                        [
                            self.store,
                            html.Div(self.store_desc, className='card-footer-desc')
                        ], 
                        width=11
                    ),
                    dbc.Col(
                        html.Div(self.button_clear, className='button_clear_div'),
                        width=1
                    )
                ],
                style=style_d
            )),
            is_open=False,
            id=self.id('footer')
        )
    
    @cached_property
    def store_desc(self): 
        return dbc.Button(
            UNFILTERED, 
            className='store_desc button_store_desc', 
            color='link',
            id=self.id(f'store_desc'),
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
            if not store_data: return UNFILTERED, False
            logger.debug('store_data_updated')
            res=self.describe_filters(store_data)
            o1 = dcc.Markdown(res.replace('[','').replace(']','')) if res else UNFILTERED
            return o1, True

    
    
    def describe_filters(self, store_data):
        # return filter_query_str(store_data)
        return ', '.join(str(x) for x in flatten_list(store_data.get(self.key,[])))






class FilterPlotCard(FilterCard):
    @cached_property
    def content(self): 
        logger.trace(self.name)
        return self.graph
    @cached_property
    def graph(self): 
        return dcc.Graph(
            figure=get_empty_fig(),
            id=self.id('graph'),
            config={'displayModeBar':False}
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
            o=self.ff().selected(selected_data)
            logger.debug(f'[{self.name}) selection updated: {o}')
            return o
        
        

















class FilterInputCard(FilterCard):
    desc = 'Filter by input'
    placeholder = 'Select'
    multi = True
    sort_by_count = True
    
    @cached_property
    def content(self): 
        logger.trace(self.name)
        return self.input
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
            self.filter_data = {self.key:vals}
            return self.filter_data
    






class MemberNameCard(FilterInputCard):
    desc = 'Filter by member name'
    placeholder='Select individual members'
    figure_factory = MemberNameFigure

class MemberDOBCard(FilterPlotCard):
    desc = 'Filter by date of birth'
    figure_factory = MemberDOBFigure    
    
class MembershipYearCard(FilterPlotCard):
    desc = 'Filter by years of membership'
    figure_factory = MembershipYearFigure    

class MemberGenderCard(FilterPlotCard):
    desc = 'Filter by gender of member'
    figure_factory = MemberGenderFigure

class MemberNationalityCard(FilterPlotCard):
    desc = 'Filter by nationality of member'
    figure_factory = MemberNationalityFigure

class MemberArrondCard(FilterPlotCard):
    desc = 'Filter by arrondissement'
    figure_factory = MemberArrondMap






class BookTitleCard(FilterInputCard):
    desc = 'Filter by book title'
    multi = True
    placeholder = 'Select books by title'
    figure_factory = BookTitleFigure


class CreatorNameCard(FilterInputCard):
    desc = 'Filter by creator'
    placeholder = 'Select books by creator'
    figure_factory = CreatorNameFigure
    

class BookYearCard(FilterPlotCard):
    desc = "Date of book's publication"
    figure_factory = BookYearFigure

class CreatorGenderCard(FilterPlotCard):
    desc = 'Filter by gender of creator'
    figure_factory = CreatorGenderFigure

class BookGenreCard(FilterPlotCard):
    desc = 'Filter by genre of book'
    figure_factory = BookGenreFigure

class CreatorNationalityCard(FilterPlotCard):
    desc = 'Filter by nationality of creator'
    figure_factory = CreatorNationalityFigure

    
class EventYearCard(FilterPlotCard):
    desc = 'Filter by year of event'
    figure_factory = EventYearFigure

class EventTypeCard(FilterPlotCard):
    desc = 'Filter by type of event'
    figure_factory = EventTypeFigure


def get_tabs(children=[], active_tab=None, tab_level=1, **kwargs):
    return dbc.Tabs(
        children=[dbc.Tab(**d) for d in children], 
        active_tab=active_tab if active_tab else (children[0].get('tab_id') if children else None), 
        id=dict(type=f'tab_level_{tab_level}', index=uid()),
        **kwargs
    )

