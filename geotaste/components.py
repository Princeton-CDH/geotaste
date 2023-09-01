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
        # self.filter_data = {}
        
        # overwritten here
        for k,v in kwargs.items(): 
            setattr(self,k,v)
        self._kwargs = kwargs

    @cached_property
    def subcomponents(self):
        return []  # subclass this
    
    def cards_with_attr(self, attrname:str):
        return [
            card
            for card in self.cards()
            if hasattr(card,attrname)
        ]

    @cached_property
    def store_subcomponents(self): 
        return self.cards_with_attr('store')
    
    @cached_property
    def store_panel_subcomponents(self): 
        return self.cards_with_attr('store_panel')
    
    @cached_property
    def graph_subcomponents(self): 
        return self.cards_with_attr('graph')
    
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
    className='collapsible-card'
    tooltip = ''

    def layout(self, params=None, header=True, body=True, footer=True, **kwargs):
        logger.trace(self.name)
        children = []
        if header and self.header is not None: children.append(self.header)
        if body and self.body is not None: children.append(self.body)
        if footer and self.footer is not None: children.append(self.footer)
        return dbc.Card(children, className=f'collapsible-card {self.className}', **kwargs)

    @cached_property
    def header(self):
        logger.trace(self.name)
        desc=self.desc[0].upper() + self.desc[1:]
        idx=self.id('card_header')
        btn_title = dbc.Button(
            desc, 
            color="link", 
            n_clicks=0,
            id=idx,
            className='card-title'
        )
        children = [
            html.Div(
                [
                    self.button_showhide
                ], 
                className='button_showhide_div'
            ),
            btn_title
        ]
        if self.tooltip:
            children.append(tooltip(btn_title, self.tooltip))
        return dbc.CardHeader(
            children,
            className=f'card-header-{self.className}'
        )
    
    @cached_property
    def body(self):
        logger.trace(self.name)
        return dbc.Collapse(
            dbc.CardBody(self.content), 
            is_open=self.body_is_open, 
            id=self.id('body'),
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
            "[+]", 
            color="link", 
            n_clicks=0,
            className='button_showhide',
            id=self.id('button_showhide')
        )
    
    def component_callbacks(self, app):       
        logger.trace(self.name) 
        ## buttons
        @app.callback(
            [
                Output(self.body, "is_open", allow_duplicate=True),
                Output(self.button_showhide, "children", allow_duplicate=True),
            ],
            [
                Input(self.button_showhide, "n_clicks"),
                Input(self.id('card_header'), 'n_clicks')
            ],
            State(self.body, "is_open"),
            prevent_initial_call=True
        )
        #@logger.catch
        def toggle_collapse(n1, n2, is_open):
            now_is_open = (not is_open if (n1 or n2) else is_open)
            logger.debug(f'{self.name} is now open? {now_is_open}')
            return now_is_open, '[–]' if now_is_open else '[+]'


@cache
@cache_obj.memoize()
def ff_cache(figure_class, serialized_data):
    logger.debug(f'ff_cache({figure_class.__name__}, {serialized_data})')
    filter_data,selected,kwargs = unserialize(serialized_data)
    return figure_class(filter_data, selected, **kwargs)


@cache
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

    def ff(self, filter_data={}, selected:dict|list={}, **kwargs):
        if self.figure_factory is not None:
            kwargs = {**self._kwargs, **kwargs}
            serialized_data = serialize([filter_data, selected, kwargs])
            return ff_cache(self.figure_factory, serialized_data)

    def plot(self, filter_data={}, existing_fig=None, min_val=None, max_val=None, **kwargs) -> go.Figure:
        ff = self.ff(filter_data)
        if min_val is not None: ff.min_series_val=min_val
        if max_val is not None: ff.min_series_val=max_val
        return ff.fig
    

    def plot1(self, filter_data={}, existing_fig=None, **kwargs) -> go.Figure:
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



        
class FilterComponent(FigureComponent):
    desc = 'X'
    unfiltered = UNFILTERED
    
    @cached_property
    def store(self):
        return dcc.Store(id=self.id('store'), data={})
    
    @cached_property
    def store_panel(self):
        return dcc.Store(id=self.id('store_panel'), data={})
    
    @cached_property
    def store_selection(self):
        return dcc.Store(id=self.id('store_selection'), data={})
    
    @cached_property
    def store_desc(self): 
        return html.Span(self.unfiltered, className='store_desc')

    def intersect_filters(self, *filters_d):
        return intersect_filters(filters_d)
    








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
                            self.store_panel,
                            self.store_selection,
                            html.Div(
                                self.store_desc, 
                                className='card-footer-desc'
                            )
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

    
    
    def describe_filters(self, store_data):
        # return filter_query_str(store_data)
        return ', '.join(str(x) for x in flatten_list(store_data.get(self.key,[])))


    # def component_callbacks(self, app):
    #     super().component_callbacks(app)

    #     @app.callback(
    #         [
    #             Output(self.store_desc, 'children', allow_duplicate=True),
    #             Output(self.footer, 'is_open', allow_duplicate=True)
    #         ],
    #         Input(self.store, 'data'),
    #         prevent_initial_call=True
    #     )
    #     #@logger.catch
    #     def store_data_updated(store_data):
    #         # filter cleared?
    #         if not store_data: return UNFILTERED, False
    #         logger.debug('store_data_updated')
    #         res=self.describe_filters(store_data)
    #         o1 = dcc.Markdown(res.replace('[','').replace(']','')) if res else UNFILTERED
    #         return o1, True




class FilterPlotCard(FilterCard):
    body_is_open = False
    @cached_property
    def content(self): 
        logger.trace(self.name)
        return self.graph
    @cached_property
    def graph(self): 
        return dcc.Graph(
            figure=get_empty_fig(),
            id=self.id('graph'),
            config={'displayModeBar':False},
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
        #@logger.catch
        def clear_selection(n_clicks):
            return {}, self.plot()
        
            
        @app.callback(
            [
                Output(self.store_desc, 'children', allow_duplicate=True),
                Output(self.footer, 'is_open', allow_duplicate=True)
            ],
            Input(self.store, 'data'),
            prevent_initial_call=True
        )
        #@logger.catchq
        def store_data_updated(store_data):
            # filter cleared?
            if not store_data: return self.unfiltered, False
            logger.debug('store_data_updated')
            res=self.describe_filters(store_data)
            o1 = dcc.Markdown(res.replace('[','').replace(']','')) if res else self.unfiltered
            return o1, True

        

        @app.callback(
            Output(self.graph, "figure", allow_duplicate=True),
            [
                Input(self.body, "is_open"),
                Input(self.store_panel, 'data')
            ],
            [
                # State(self.graph, 'figure'),
                # State(self.store_selection, 'data')
                State(self.store, 'data')
            ],
            prevent_initial_call=True
        )
        #@logger.catch
        def toggle_collapse(is_open, panel_filter_data, my_filter_data):
            # logger.debug(f'{self.name} is now open? {is_open}')
            if not is_open: return dash.no_update
            
            filter_data={
                k:v 
                for k,v in panel_filter_data.items() 
                if k not in my_filter_data
                and k != self.key
            }
            ff = self.ff(filter_data, selected=my_filter_data)
            return ff.fig



        @app.callback(
            Output(self.store, "data", allow_duplicate=True),
            Input(self.graph, 'selectedData'),
            State(self.store, 'data'),
            prevent_initial_call=True
        )
        #@logger.catch
        def graph_selection_updated(selected_data, old_data={}):
            logger.debug(f'[{self.name}) selection updated 1: {selected_data}')
            o=self.ff().selected(selected_data)
            if not o: raise PreventUpdate
            out=(o if o!=old_data else dash.no_update)
            logger.debug(f'[{self.name}) selection updated 2: {out}')
            return out
        
        
class FilterSliderCard(FilterCard):
    value=None
    unfiltered=''
    body_is_open = False


    @cached_property
    def graph(self): 
        return dcc.Graph(
            # figure=self.ff().plot(),
            figure=get_empty_fig(),
            id=self.id('graph'),
            config={'displayModeBar':False},
        )

    @cached_property
    def minval(self):
        return self.ff().series_q.min()
    @cached_property
    def maxval(self):
        return self.ff().series_q.max()
    
    @cached_property
    def content(self): 
        logger.trace(self.name)
        return dbc.Container([
            dbc.Row(self.graph),
            dbc.Row([
                dbc.Col(self.input_start),
                dbc.Col(self.input_end, style={'text-align':'right'})
            ])
        ])

    @cached_property
    def input_start(self):
        return dcc.Input(
            type="number", 
            min=self.minval, 
            max=self.maxval, 
            value=self.minval if self.value is None else self.value,
            className='slider-input-num'
        )
    
    @cached_property
    def input_end(self):
        return dcc.Input(
            type="number", 
            min=self.minval, 
            max=self.maxval, 
            value=self.maxval if self.value is None else self.value,
            className='slider-input-num',
            style={'text-align':'right'}
        )
    
    def describe_filters(self,store_data):
        vals=list(store_data.values())[0]
        minval=min(vals) if vals else self.minval
        maxval=max(vals) if vals else self.maxval
        return f'{minval} to {maxval}'
    

    def component_callbacks(self, app):
        super().component_callbacks(app)

        @app.callback(
            Output(self.footer, 'is_open', allow_duplicate=True),
            Input(self.store, 'data'),
            prevent_initial_call=True
        )
        #@logger.catch
        def store_data_updated(store_data):
            # filter cleared?
            if not store_data: return False
            return True

        @app.callback(
            [
                Output(self.graph, 'figure', allow_duplicate=True),
                Output(self.input_start, 'value', allow_duplicate=True),
                Output(self.input_end, 'value', allow_duplicate=True),
                Output(self.store, "data", allow_duplicate=True),
                Output(self.store_desc, 'children', allow_duplicate=True)
            ],
            [
                Input(self.graph, 'selectedData'),
                Input(self.input_start, 'value'),
                Input(self.input_end, 'value'),
                Input(self.button_clear, 'n_clicks'),
                Input(self.body, "is_open"),
            ],
            [
                State(self.store, 'data'),
                State(self.graph, 'figure'),
                State(self.store_desc, 'children')
            ],
            prevent_initial_call=True
        )
        def graph_selection_updated(
                selected_data,
                start_value,
                end_value,
                clear_clicked,
                body_open_now,
                old_data={},
                old_fig=None,
                old_desc=''
            ):
            def vstr(x): return f'{int(x)}' if x is not None else ''

            logger.debug(['sel updated on slider!', ctx.triggered_id, ctx.triggered])

            if ctx.triggered_id == self.graph.id:
                logger.debug(f'GRAPH TRIGGERED: {len(selected_data)} len sel data')
                new_data=self.ff().selected(selected_data)
                if not new_data or new_data==old_data: raise PreventUpdate

                vals=list(new_data.values())
                minval=min(vals[0]) if vals else None
                maxval=max(vals[0]) if vals else None
                o=[
                    old_fig, 
                    minval, 
                    maxval, 
                    new_data, 
                    f'{vstr(minval)} – {vstr(maxval)}'
                ]
            
            elif ctx.triggered_id in {self.body.id, self.input_start.id, self.input_end.id}:
                if body_open_now:
                    logger.debug(f'INPUT TRIGGERED TRIGGERED')
                    ff = self.ff(min_series_val=start_value, max_series_val=end_value)
                    newfig = ff.plot()
                    o=[
                        newfig, 
                        start_value, 
                        end_value, 
                        ff.seldata if ctx.triggered_id!=self.body.id else old_data,
                        f'{vstr(start_value)} – {vstr(end_value)}' if ctx.triggered_id!=self.body.id else old_desc,
                    ]
            
            elif ctx.triggered_id == self.button_clear.id and clear_clicked:
                ff=self.ff()
                o=[ff.plot(), ff.minval, ff.maxval, {}, '']
            
            else:
                logger.debug('not updating')
                raise PreventUpdate
            
            logger.debug(['graph_selection_updated->',o])
            return o

                
    


















class FilterInputCard(FilterCard):
    desc = 'input'
    placeholder = 'Select'
    multi = True
    sort_by_count = True
    
    @cached_property
    def content(self): 
        logger.trace(self.name)
        return self.input
    @cached_property
    def input(self):
        l=self.ff().unique(sort_by_count=self.sort_by_count)
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

        # @app.callback(
        #     Output(self.graph, "figure", allow_duplicate=True),
        #     [
        #         Input(self.body, "is_open"),
        #         Input(self.store_panel, 'data')
        #     ],
        #     [
        #         # State(self.graph, 'figure'),
        #         # State(self.store_selection, 'data')
        #         State(self.store, 'data')
        #     ],
        #     prevent_initial_call=True
        # )
        # #@logger.catch
        # def toggle_collapse(is_open, panel_filter_data, my_filter_data):
        #     # logger.debug(f'{self.name} is now open? {is_open}')
        #     if not is_open: return dash.no_update
            
        #     filter_data={
        #         k:v 
        #         for k,v in panel_filter_data.items() 
        #         if k not in my_filter_data
        #         and k != self.key
        #     }
        #     ff = self.ff(filter_data, selected=my_filter_data)
        #     return ff.fig

        # ## CLEAR? -- OVERWRITTEN
        @app.callback(
            [
                Output(self.store, "data", allow_duplicate=True),
                Output(self.input, "value", allow_duplicate=True),
            ],
            Input(self.button_clear, 'n_clicks'),
            prevent_initial_call=True
        )
        #@logger.catch
        def clear_selection(n_clicks):
            logger.debug('clear_selection')
            return {}, []
        
        @app.callback(
            [
                Output(self.store_desc, 'children', allow_duplicate=True),
                Output(self.footer, 'is_open', allow_duplicate=True)
            ],
            Input(self.store, 'data'),
            prevent_initial_call=True
        )
        #@logger.catchq
        def store_data_updated(store_data):
            # filter cleared?
            if not store_data: return self.unfiltered, False
            logger.debug('store_data_updated')
            res=self.describe_filters(store_data)
            o1 = dcc.Markdown(res.replace('[','').replace(']','')) if res else self.unfiltered
            return o1, True

        @app.callback(
            Output(self.store, "data", allow_duplicate=True),
            Input(self.input, 'value'),
            prevent_initial_call=True
        )
        #@logger.catch
        def input_value_changed(vals):
            if not vals: raise PreventUpdate
            filter_data = {self.key:vals}
            return filter_data
    

        @app.callback(
            Output(self.input, "options", allow_duplicate=True),
            [
                Input(self.body, "is_open"),
                Input(self.store_panel, 'data')
            ],
            [
                State(self.store, 'data')
            ],
            prevent_initial_call=True
        )
        #@logger.catch
        def update_input_vals(is_open, panel_filter_data, my_filter_data):
            if not is_open: return dash.no_update            
            filter_data={
                k:v 
                for k,v in panel_filter_data.items() 
                if k not in my_filter_data
                and k != self.key
            }
            ff = self.ff(filter_data)
            return ff.unique(sort_by_count=self.sort_by_count)






class MemberNameCard(FilterInputCard):
    desc = 'Name'
    placeholder='Select individual members'
    figure_factory = MemberNameFigure
    # tooltip = 'Filter for particular members by name'

class MemberDOBCard(FilterSliderCard):
    desc = 'Birth year'
    figure_factory = MemberDOBFigure 
    # tooltip = 'Filter members by date of birth'   
    
class MembershipYearCard(FilterSliderCard):
    desc = 'Years active'
    figure_factory = MembershipYearFigure    
    # tooltip = 'Filter for membership by years of active members'

class MemberGenderCard(FilterPlotCard):
    desc = 'Gender'
    figure_factory = MemberGenderFigure
    # tooltip = 'Filter for members by genre'

class MemberNationalityCard(FilterPlotCard):
    desc = 'Nationality'
    figure_factory = MemberNationalityFigure
    # tooltip = 'Filter for members of particular nationalities'

class MemberArrondCard(FilterPlotCard):
    desc = 'Arrondissement'
    figure_factory = MemberArrondMap
    # tooltip = 'Filter for members who ever lived in a given arrondissement'






class BookTitleCard(FilterInputCard):
    desc = 'Title'
    multi = True
    placeholder = 'Select books by title'
    figure_factory = BookTitleFigure
    # tooltip = 'Filter for particular books'

class CreatorNameCard(FilterInputCard):
    desc = 'Author'
    placeholder = 'Select books by creator'
    figure_factory = CreatorNameFigure
    # tooltip = 'Filter for particular authors'

class BookYearCard(FilterSliderCard):
    desc = "Publication date"
    figure_factory = BookYearFigure
    # tooltip = 'Filter by when the borrowed book was published'

class CreatorGenderCard(FilterPlotCard):
    desc = 'Author gender'
    figure_factory = CreatorGenderFigure
    # tooltip = 'Filter by the gender of the author'

class BookGenreCard(FilterPlotCard):
    desc = 'Genre'
    figure_factory = BookGenreFigure
    # tooltip = 'Filter by genre of book'

class CreatorNationalityCard(FilterPlotCard):
    desc = 'Author nationality'
    figure_factory = CreatorNationalityFigure
    # tooltip = 'Filter by the nationality of the author'

    
class EventYearCard(FilterSliderCard):
    desc = 'Year of borrowing'
    figure_factory = EventYearFigure
    # tooltip = 'Filter for the books borrowed in a given year range'

class EventMonthCard(FilterSliderCard):
    desc = 'Month of borrowing'
    figure_factory = EventMonthFigure
    # tooltip = 'Filter for the books borrowed in a given month range (showing seasonal effects)'

class EventTypeCard(FilterPlotCard):
    desc = 'type of event'
    figure_factory = EventTypeFigure


def get_tabs(children=[], active_tab=None, tab_level=1, **kwargs):
    tabs = [
        dbc.Tab(
            children=d.get('children'),
            label=d.get('label'),
            tab_id=d.get('tab_id'),
            id=d.get('id', uid())
        )
        for d in children
    ]
    tooltips = [
        tooltip(tab, d.get('tooltip'))
        for tab,d in zip(tabs,children)
        if d.get('tooltip')
    ]
    active_tab=(
        active_tab 
        if active_tab 
        else (
            children[0].get('tab_id') 
            if children 
            else None
        )
    )
    
    tabs_obj = dbc.Tabs(
        children=tabs, 
        active_tab=active_tab, 
        id=dict(
            type=f'tab_level_{tab_level}', 
            index=uid()
        ),
        **kwargs
    )
    return dbc.Container([tabs_obj] + tooltips)



def tooltip(component, tooltip=''):
    return dbc.Tooltip(tooltip, target=component.id)





def get_welcome_modal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(WELCOME_HEADER)),
            dbc.ModalBody([
                html.H3(WELCOME_HEADER2),
                html.Br(),
                html.P(WELCOME_BODY),
            ])
        ],
        id="welcome-modal",
        centered=True,
        is_open=WELOME_MSG_ON,
        size='lg'
    )


