"""
All the classes and functions for making the base dash components for the Dash app. Panel components are in `panels.py`. Most of these classes have a `figure_factory` attached, such that `component.ff(filter_data)` will return an instance of that component's figure directory with that filter data. They rely on the `Dataset` classes in dataset.py and use plotly to plot figures. For example, `MemberNationalityCard` has a `figure_factory` attribute pointing to `MemberNationalityFigure`.

The base class is in `BaseComponent`, which defines the default behavior of all components used in this app, including in `panels.py`. `FilterComponent` is a subclass of `BaseComponent`, adding `.store` and other filter-saving attributes; `FilterCard` a further subclass, allowing for opening/collapsing. `FilterPlotCard` extends `FilterCard` to allow graphing; `FilterSliderCard` adds graphing and numerical inputs for slider plots; and `FilterInputCard` adds a dropdown with input.
"""


from .imports import *


class BaseComponent(DashComponent):
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
        # self.color = None
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
            for card in self.subcomponents
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
        return self.get_content()
    
    def get_content(self, params=None, **kwargs): 
        logger.debug(f'[{self.name}] component getting content')
        return dbc.Container(
            BLANK if not self.subcomponents else [
            card.layout(params) 
            for card in self.subcomponents
        ])
        
    
    def layout(self, params=None): 
        logger.debug(f'[{self.name}].layout()...')
        return self.content
    


        
class FilterComponent(BaseComponent):
    desc = 'X'
    unfiltered = UNFILTERED
    figure_factory = None
    records_name='members'
    
    @cached_property
    def store(self):
        return dcc.Store(id=self.id('store'), data={})
    
    @cached_property
    def store_json(self):
        return dcc.Store(id=self.id('store_json'), data='')
    
    @cached_property
    def store_panel(self):
        return dcc.Store(id=self.id('store_panel'), data={})
    
    # @cached_property
    # def store_selection(self):
    #     return dcc.Store(id=self.id('store_selection'), data={})
    
    @cached_property
    def store_desc(self): 
        return html.Span(BLANK, className='store_desc')

    def intersect_filters(self, *filters_d):
        return intersect_filters(filters_d)
    
    def ff(self, filter_data={}, selected:list=[], **kwargs):
        # if self.figure_factory is not None:
        #     kwargs = {**self._kwargs, **kwargs}
        #     serialized_data = serialize([filter_data, selected, kwargs])
        #     return ff_cache(self.figure_factory, serialized_data)
        logger.trace(f'[{self.name}.ff({filter_data}, {selected}, **{kwargs})]')


        filter_data={
            k:v 
            for k,v in filter_data.items() 
            if k not in set(selected)
            and k != self.key
        }


        return self.figure_factory(
            filter_data=filter_data, 
            selected=selected, 
            **kwargs
        )

    def plot(self, filter_data={}, existing_fig=None, min_val=None, max_val=None, **kwargs) -> go.Figure:
        ff = self.ff(filter_data)
        if min_val is not None: ff.min_series_val=min_val
        if max_val is not None: ff.min_series_val=max_val
        # return ff.fig
        return ff.plot(**kwargs)

    @cached_property
    def series(self): return self.ff().series
    @cached_property
    def key(self): 
        try:
            return self.figure_factory.key
        except AttributeError:
            return None




class FilterCard(FilterComponent):
    body_is_open = False
    className='collapsible-card'
    tooltip = ''

    def layout(self, params=None):
        return dbc.Card([
            self.header,
            self.footer,
            self.body,

            # data
            self.store, 
            self.store_json,
            self.store_panel,
            # self.store_selection,

        ], className=f'collapsible-card {self.className}')


    @cached_property
    def header(self):
        logger.trace(self.name)
        return dbc.CardHeader(
            [
                self.showhide_btn,
                self.header_btn, 
            ],
            className=f'card-header-{self.className}'
        )
    
    @cached_property
    def header_btn(self):
        return dbc.Button(
            self.desc[0].upper() + self.desc[1:],
            color="link",
            n_clicks=0,
            id=self.id('header_btn'),
            className='card-title'
        )
    
    @cached_property
    def showhide_btn(self):
        logger.trace(self.name)
        return dbc.Button(
            "[+]", 
            color="link", 
            n_clicks=0,
            className='button_showhide',
            id=self.id('button_showhide')
        )
    
    
    
    
    ## Body
    
    @cached_property
    def body(self):
        logger.trace(self.name)
        return dbc.Collapse(
            dbc.CardBody(self.content), 
            is_open=self.body_is_open, 
            id=self.id('body'),
        )
    
    
    


    ## footer
    
    
    @cached_property
    def footer(self):
        logger.trace(self.name)
        style_d={'color':self.color if self.color else 'inherit', 'font-size':'.8em'}
        return dbc.Collapse(
            dbc.CardFooter([
                self.store_desc, 
                self.button_clear,
                ],
                style=style_d
            ),
            is_open=False,
            id=self.id('footer')
        )
    
    @cached_property
    def store_desc(self): 
        return html.Span(
            BLANK, 
            className='store_desc button_store_desc', 
            # color='link',
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
        vals=', '.join(str(x) for x in flatten_list(store_data.get(self.key,[])))
        return vals


    def component_callbacks(self, app):
        super().component_callbacks(app)

        @app.callback(
            [
                Output(self.body, "is_open", allow_duplicate=True),
                Output(self.showhide_btn, "children", allow_duplicate=True),
                Output(self.content, 'children', allow_duplicate=True),
                # Output(self.store_json, "data", allow_duplicate=True),
            ],
            [
                Input(self.showhide_btn, "n_clicks"),
                Input(self.header_btn, 'n_clicks'),
            ],
            [
                State(self.body, "is_open"),
                State(self.content,'children'),
                # State(self.store_json, 'data'),
                State(self.store, 'data'),
                State(self.store_panel, 'data'),
                
            ],
            prevent_initial_call=True
        )
        #@logger.catch
        def toggle_collapse(_clicked1, _clicked2, body_open_now, content_now, card_data, panel_data):
            """Toggle the collapse state of a section.
            
            Args:
                _clicked1 (any): The first clicked parameter.
                _clicked2 (any): The second clicked parameter.
                body_open_now (bool): The current state of the body.
                content_now (any): The current content.
            
            Returns:
                tuple: A tuple containing the new state of the body (bool), the new toggle symbol (str), and the new content (any).
            """
            
            if body_open_now:
                # then we're going to shut
                logger.debug(f'[{self.name}] toggle_collapse: closing')
                return False, '[+]', content_now
            else:
                # then we're going to open
                logger.debug(f'[{self.name}] toggle_collapse: opening')
                # logger.debug(content_now)
                content_exists_already = bool(content_now)# and content_now[0].get('props',{}).get('children')
                logger.debug(f'content currently exists? --> {content_exists_already}, {len(str(content_now))}')


                return True, '[-]', content_now if content_exists_already else self.get_content(
                    card_data=card_data,
                    panel_data=panel_data
                )


            # return now_is_open, '[–]' if now_is_open else '[+]', content_now if content_now else self.get_content()
        
        @app.callback(
            [
                Output(self.store_desc, 'children', allow_duplicate=True),
                Output(self.footer, 'is_open', allow_duplicate=True),
            ],
            Input(self.store, 'data'),
            prevent_initial_call=True
        )
        #@logger.catchq
        def toggle_footer_storedesc(store_data):
            # filter cleared?
            logger.trace(f'[{self.name}] my card data updated, so I\'ll update my store_desc and open footer')
            if not store_data: 
                return BLANK, False
            else:
                res=self.describe_filters(store_data)
                return res if res else BLANK, True
        


        @app.callback(
            Output(self.store, "data", allow_duplicate=True),
            Input(self.button_clear, 'n_clicks'),
            prevent_initial_call=True
        )
        #@logger.catch
        def clear_selection(n_clicks):
            logger.debug(f'[{self.name}] clearing selection v1')
            return {}


class FilterPlotCard(FilterCard):
    body_is_open = False

    @cached_property
    def content(self,params=None):
        return dbc.Container(self.graph)

    @cached_property
    def graph(self): 
        return dcc.Graph(
            figure=get_empty_fig(),
            id=self.id('graph'),
            config={'displayModeBar':False},
        )
    
    def plot(self, filter_data={}, selected=[], **kwargs):
        return plot_cache(
            self.figure_factory,
            serialize([
                filter_data,
                selected,
                {**kwargs, **{'color':self.color}}
            ])
        )
    

    def component_callbacks(self, app):
        # do my parent's too
        super().component_callbacks(app)
        
        @app.callback(
            Output(self.store, "data", allow_duplicate=True),
            Input(self.graph, 'selectedData'),
            State(self.store, 'data'),
            prevent_initial_call=True
        )
        #@logger.catch
        def graph_selection_updated(selected_data, old_data={}):
            if selected_data is None: raise PreventUpdate
            o=self.ff().get_selected(selected_data)
            if not o or o==old_data: raise PreventUpdate
            if type(o)==dict and not o.get(self.key): raise PreventUpdate
            logger.debug(f'[{self.name}) selection updated to {o}')
            return o
        
        
        @app.callback(
            Output(self.store_json, "data", allow_duplicate=True),
            Input(self.body, "is_open"),
            [
                State(self.store_json, "data"),
                State(self.store, "data"),
                State(self.store_panel, "data"),
            ],
            prevent_initial_call=True
        )
        def draw(is_open,json_now, my_filter_data, panel_filter_data):
            if not is_open or json_now: raise PreventUpdate
            newdata = {k:v for k,v in panel_filter_data.items() if k not in my_filter_data}
            ofig_json_gz_str=self.plot(newdata, selected=my_filter_data)
            return ofig_json_gz_str
            
            
        @app.callback(
            [
                Output(self.store_json, "data", allow_duplicate=True),
                Output(self.store, 'data', allow_duplicate=True)
            ],
            [
                Input(self.store_panel, 'data'),
            ],
            [
                State(self.store, 'data'),
                State(self.showhide_btn, "n_clicks"),
                State(self.header_btn, 'n_clicks'),
                State(self.graph, 'selectedData')
            ],
            prevent_initial_call=True
        )
        def panel_data_updated(panel_filter_data, my_filter_data, _clicked_open_1,_clicked_open_2, current_sels):
            if not _clicked_open_1 and not _clicked_open_2: raise PreventUpdate
            logger.debug(f'triggered by {ctx.triggered_id}, with panel_filter_data = {panel_filter_data} and my_filter_data = {my_filter_data}')
            if not panel_filter_data:
                # then a panel wide clear?
                my_filter_data = {}


            newdata = {k:v for k,v in panel_filter_data.items() if k not in my_filter_data}
            logger.debug(f'[{self.name}] incoming panel data: {newdata}')
            ofig_json_gz_str=self.plot(newdata, selected=my_filter_data)
            logger.debug(f'Assigning a json string of size {sys.getsizeof(ofig_json_gz_str)} compressed, to self.store_json')
            odat=my_filter_data if not panel_filter_data else dash.no_update
            return ofig_json_gz_str,odat
        
        app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='decompress'
            ),
            Output(self.graph, 'figure', allow_duplicate=True),
            Input(self.store_json, 'data'),
            prevent_initial_call=True
        )



        
        
class FilterSliderCard(FilterPlotCard):
    value=None
    unfiltered=''
    body_is_open = False

    @cached_property
    def content(self, card_data={}, panel_data={}, selected=[], **kwargs):
        return dbc.Container([
            dbc.Row(self.graph),
            dbc.Row([
                dbc.Col(self.input_start, width=3),
                dbc.Col('–', width=1),
                dbc.Col(self.input_end, width=3),
                dbc.Col(self.input_btn, width=5, style={'text-align':'right'})
            ], className='slider-row')
        ], className='slider-container')

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
    def input_start(self):
        return dcc.Input(
            type="number", 
            value=0 if self.minval is None else self.minval,
            className='slider-input-num',
            id=self.id('input_start')
        )
    
    @cached_property
    def input_end(self):
        return dcc.Input(
            type="number", 
            value=0 if self.maxval is None else self.maxval,
            className='slider-input-num',
            id=self.id('input_end')
        )
    
    @cached_property
    def input_btn(self):
        return dbc.Button(
            'Set',
            color="link",
            n_clicks=0,
            id=self.id('input_btn'),
            className='slider-input-btn'
        )
    
    def describe_filters(self,store_data):
        vals=list(store_data.values())[0]
        minval=min(vals) if vals else self.minval
        maxval=max(vals) if vals else self.maxval
        return f'{minval} to {maxval}'
    

    def component_callbacks(self, app):
        super().component_callbacks(app)

        @app.callback(
            [
                Output(self.store_json,'data',allow_duplicate=True),
                Output(self.store,'data',allow_duplicate=True),
                Output(self.id('input_start'), 'value',allow_duplicate=True),
                Output(self.id('input_end'), 'value',allow_duplicate=True),
            ],
            [
                Input(self.graph, 'selectedData'),
                Input(self.id('input_btn'), 'n_clicks'),
            ],
            [
                State(self.id('input_start'), 'value'),
                State(self.id('input_end'), 'value'),
                State(self.store_panel,'data'),
                # State(self.graph,'figure')
            ],
            prevent_initial_call=True
        )
        def graph_selection_updated2(graph_selected_data, btn_clk, start_value, end_value, panel_data):
            logger.debug(f'graph_selected_data = {graph_selected_data}')
            if ctx.triggered_id == self.graph.id:
                seldata=self.ff().get_selected(graph_selected_data)
                logger.debug(f'seldata = {seldata}')
                if not seldata or not seldata.get(self.key): raise PreventUpdate

                vals=list(seldata.values())
                logger.debug(f'vals = {vals}')
                minval=min(vals[0]) if vals and vals[0] else 0
                maxval=max(vals[0]) if vals and vals[0] else 0
                return dash.no_update,dash.no_update,minval,maxval
            else:
                newvals=list(range(start_value, end_value+1))
                ofig_json_gz_str = self.plot(
                    filter_data=panel_data if panel_data else {},
                    selected=newvals
                )
                odat = {self.figure_factory.key:newvals}
                return ofig_json_gz_str,odat,dash.no_update,dash.no_update
            
        @app.callback(
            [
                Output(self.id('input_start'), 'value',allow_duplicate=True),
                Output(self.id('input_end'), 'value',allow_duplicate=True),
            ],
            Input(self.button_clear, 'n_clicks'),
            State(self.store_panel, 'data'),
            prevent_initial_call=True
        )
        def clear_selection_inputs(clear_clicked, panel_data):
            if not clear_clicked: raise PreventUpdate
            ff=self.ff(panel_data)
            return ff.minval, ff.maxval

                



class FilterInputCard(FilterCard):
    desc = 'input'
    placeholder = 'Select'
    multi = True
    sort_by_count = True
    
    def get_content(self,**y): 
        logger.debug(f'[{self.name}] getting content for input card')
        return dbc.Container(self.input)

    @cached_property
    def input(self):
        l=self.ff().get_unique_vals(sort_by_count=self.sort_by_count)
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

        @app.callback(
            Output(self.store, "data", allow_duplicate=True),
            Input(self.input, 'value'),
            prevent_initial_call=True
        )
        def input_value_changed(vals):
            if not vals: raise PreventUpdate
            logger.debug(f'[{self.name}] {self.key} -> {vals}')
            return {self.key:vals}
        
        # Clear part 2
        @app.callback(
            Output(self.input,'value'),
            Input(self.button_clear, 'n_clicks'),
            prevent_initial_call=True
        )
        #@logger.catch
        def clear_selection_input(n_clicks):
            logger.debug('clear_selection as input')
            return []





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
    figure_factory = MemberArrondFigure
    # tooltip = 'Filter for members who ever lived in a given arrondissement'






class BookTitleCard(FilterInputCard):
    desc = 'Title'
    multi = True
    placeholder = 'Select books by title'
    figure_factory = BookTitleFigure
    # tooltip = 'Filter for particular books'

class AuthorNameCard(FilterInputCard):
    desc = 'Author'
    placeholder = 'Select books by creator'
    figure_factory = AuthorNameFigure
    # tooltip = 'Filter for particular authors'

class BookYearCard(FilterSliderCard):
    desc = "Publication date"
    figure_factory = BookYearFigure
    # tooltip = 'Filter by when the borrowed book was published'

class AuthorGenderCard(FilterPlotCard):
    desc = 'Author gender'
    figure_factory = AuthorGenderFigure
    # tooltip = 'Filter by the gender of the author'

class BookGenreCard(FilterPlotCard):
    desc = 'Genre'
    figure_factory = BookGenreFigure
    # tooltip = 'Filter by genre of book'

class AuthorNationalityCard(FilterPlotCard):
    desc = 'Author nationality'
    figure_factory = AuthorNationalityFigure
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


