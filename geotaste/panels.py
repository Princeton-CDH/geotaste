from .imports import *
from .views import *


class FilterPanel(FilterCard):
    unfiltered = UNFILTERED

    # @cached_property
    # def content(self,params=None):
    #     return dbc.Container([self.store] + super().content.children)
    
    # # @cached_property
    # # def store_desc(self): 
    # #     return html.Span(
    # #         self.unfiltered,
    # #         id=self.id('query_str'), 
    # #         className='store_desc query_str', 
    # #         # placeholder=UNFILTERED, 
    # #         # value='', 
    # #         # style={'color':self.color}
    # #     )


    # def component_callbacks(self, app):
    #     super().component_callbacks(app)
        
    #     # intersect and listen
    #     if self.store_subcomponents:
    #         @app.callback(
    #             Output(self.store, 'data', allow_duplicate=True),
    #             [
    #                 Input(card.store, 'data')
    #                 for card in self.store_subcomponents
    #             ],
    #             prevent_initial_call=True
    #         )
    #         def subcomponent_filters_updated(*filters_d):
    #             logger.debug('subcomponent filters updated')
    #             return self.intersect_filters(*filters_d)
            
    #         @app.callback(
    #             [
    #                 Output(card.store_panel, 'data', allow_duplicate=True)
    #                 for card in self.store_panel_subcomponents
    #             ],
    #             Input(self.store, 'data'),
    #             [
    #                 State(card.store_panel, 'data')
    #                 for card in self.store_panel_subcomponents
    #             ],
    #             prevent_initial_call=True
    #         )
    #         #@logger.catch
    #         def panel_filter_data_changed(panel_filter_data, *old_filter_data_l):
    #             if panel_filter_data is None: panel_filter_data={}
    #             logger.debug(f'panel_filter_data_changed({panel_filter_data})')


    #             logger.debug([card.key for card in self.store_panel_subcomponents])

    #             new_filter_data_l = [
    #                 {k:v for k,v in panel_filter_data.items() if k!=card.key}
    #                 for card in self.store_panel_subcomponents    
    #             ]
    #             out = [
    #                 (dash.no_update if old==new else new)
    #                 for old,new in zip(old_filter_data_l, new_filter_data_l)
    #             ]
    #             logger.trace(f'out from panel {pformat(out)}')
    #             return out
            

            

  

class MemberPanel(FilterPanel):
    name='MP'
    figure_factory = CombinedFigureFactory
    desc = 'Members of the library'
    records_name='members'
    # tooltip = 'Filter members of the library by name, date of birth, when active, gender, nationality, and arrondissement'

    @cached_property
    def name_card(self): 
        return MemberNameCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def dob_card(self): 
        return MemberDOBCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def membership_year_card(self): 
        return MembershipYearCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def gender_card(self): 
        return MemberGenderCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def nation_card(self): 
        return MemberNationalityCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def arrond_card(self): 
        return MemberArrondCard(name_context=self.name, **self._kwargs)

    @cached_property
    def subcomponents(self):
        return [
            self.name_card,
            self.membership_year_card,
            self.dob_card,
            self.gender_card,
            self.nation_card,
            self.arrond_card,
        ]

    @cached_property
    def store_subcomponents(self): return []
    @cached_property
    def graph_subcomponents(self): return []
    
    

class BookPanel(FilterPanel):
    name='BP'
    figure_factory = CombinedFigureFactory
    desc = 'Books they borrowed'
    records_name='books'
    # tooltip = 'Filter books borrowed by title, date of publication, genre, author, author gender, author nationality, and the date borrowed'

    @cached_property
    def title_card(self): 
        return BookTitleCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def year_card(self): 
        return BookYearCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def genre_card(self): 
        return BookGenreCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def creator_card(self):
        return CreatorNameCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def creator_gender_card(self):
        return CreatorGenderCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def creator_nationality_card(self):
        return CreatorNationalityCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def event_year_card(self): 
        return EventYearCard(name_context=self.name, **self._kwargs)
    
    @cached_property
    def event_month_card(self): 
        return EventMonthCard(name_context=self.name, **self._kwargs)
        
    @cached_property
    def subcomponents(self):
        return [
            self.title_card,
            self.year_card,
            self.genre_card,
            self.creator_card,
            self.creator_gender_card,
            self.creator_nationality_card,
            self.event_year_card,
            self.event_month_card,
        ]

    @cached_property
    def store_subcomponents(self): return []
    @cached_property
    def graph_subcomponents(self): return []
    
    



class CombinedPanel(FilterPanel):
    name = 'CombinedPanel'
    desc = 'Combined Panel'
    
    @cached_property
    def member_panel(self): 
        return MemberPanel(name_context=self.name, **self._kwargs)

    @cached_property
    def book_panel(self):
        return BookPanel(name_context=self.name, **self._kwargs)
    

    @cached_property
    def subcomponents(self):
        return [
            self.member_panel,
            self.book_panel,
        ]
    
    def cards_with_attr(self, attrname:str):
        return [
            card
            for panel in self.subcomponents
            for card in panel.subcomponents
            if hasattr(card,attrname)
        ]
    



class LeftPanel(CombinedPanel):
    name='Filter 1'
    desc='Filter 1'
    L_or_R='L'
    color=LEFT_COLOR
    unfiltered=UNFILTERED_L

class RightPanel(CombinedPanel):
    name='Filter 2'
    desc='Filter 2'
    L_or_R='R'
    color=RIGHT_COLOR
    unfiltered=UNFILTERED_R







class ComparisonPanel(BaseComponent):
    figure_factory = ComparisonFigureFactory


    def layout(self, params=None):
        return dbc.Container([
            self.panel_L_col, 
            self.panel_R_col,
            self.mainview,
            ], 
            className='filters-container'
        )

    
    @cached_property
    def panel_L_col(self):
        return dbc.Container(
            [dbc.Row(self.L.layout())], 
            className='panel_L panel',
            id='panel_L'
        )
    
    @cached_property
    def panel_R_col(self):
        return dbc.Container(
            [dbc.Row(self.R.layout())],
            className='panel_R panel',
            id='panel_R'
        )


    @cached_property
    def subcomponents(self): return (self.L, self.R)

    @cached_property
    def L(self): 
        return LeftPanel()
    
    @cached_property
    def R(self): 
        return RightPanel()
    
        
    @cached_property
    def mainview(self):
        return dbc.Container('l0@didng ... ' * 100, className='mainview')


    def component_callbacks(self, app):
        super().component_callbacks(app)

        


    # def component_callbacks(self, app):
    #     super().component_callbacks(app)

    #     @app.callback(
    #         [
    #             Output(self.content_left, 'is_open', allow_duplicate=True),                      # dropdowns open
    #             # Output(self.storedesc_R_col, 'style', allow_duplicate=True),                     # whether right filter button visible
    #             Output(self.panel_R_col, 'style', allow_duplicate=True),                         # whether right filter panel visible
    #             Output(self.graphtab, 'children', allow_duplicate=True),   # actual content
    #             Output('layout-loading', 'children') # spinner
    #         ],
    #         [
    #             Input(self.L.store, 'data'),                               # any changes in left filter
    #             Input(self.R.store, 'data'),                               # any in right filter
    #             Input(self.storedesc_L_btn, "n_clicks"),
    #             Input(self.storedesc_R_btn, "n_clicks"),
    #             Input(self.graphtabs, 'active_tab')
    #         ],
    #         [
    #             State(self.content_left, 'is_open'),
    #             State(self.L.store, 'data'),
    #             State(self.R.store, 'data'),

    #         ],
    #         prevent_initial_call=True
    #     )
    #     def determine_dropdown_and_view(
    #             fdL, 
    #             fdR, 
    #             storedesc_L_clicked, 
    #             storedesc_R_clicked, 
    #             active_tab, 
    #             filter_dropdown_open_now,
    #             old_fdL,
    #             old_fdR,
    #             ):
    #         input_ids = [
    #             self.L.store.id, 
    #             self.R.store.id, 
    #             self.storedesc_L_btn.id, 
    #             self.storedesc_R_btn.id, 
    #             self.graphtabs.id
    #         ]
    #         outs = [
    #             dash.no_update,  # both dropdown vis
    #             # dash.no_update,  # right vis
    #             # dash.no_update,  # right vis
    #             # STYLE_VIS if fdL and storedesc_R_clicked else STYLE_VIS,
    #             # STYLE_VIS,
    #             STYLE_VIS if fdL and storedesc_R_clicked else STYLE_INVIS,
    #             dash.no_update   # content,
    #         ]
            
    #         logger.debug(ctx.triggered)
    #         logger.debug(input_ids)

    #         # if we clicked the Left or Right top Filter tab button
    #         if ctx.triggered_id in {self.storedesc_L_btn.id, self.storedesc_R_btn.id}:
    #             if storedesc_R_clicked!=1:
    #                 outs[0]=not filter_dropdown_open_now

    #         # if the tab changed -- or the filters changed
    #         elif ctx.triggered_id in {self.graphtabs.id, self.L.store.id, self.R.store.id}:

    #             # make sure change actually happened?
    #             args = [[active_tab],[],fdL,fdR]
    #             logger.debug(['switchtab'] + args)
    #             logger.debug([fdL, old_fdL])
    #             logger.debug([fdR, old_fdR])
    #             serialized_data = serialize(args)
    #             outs[-1] = graphtab_cache(serialized_data)

    #             # also collapse dropdowns if tab changed
    #             # if ctx.triggered_id == self.graphtabs.id:
    #                 # outs[0] = False
            
    #         # logger.debug(outs)
    #         return outs + [True]



        
            

# @cache
# @cache_obj.memoize()
def graphtab_cache(serialized_data):
    logger.trace(f'graphtab_cache({serialized_data})')
    tab_ids_1, tab_ids_2, fdL, fdR = unserialize(serialized_data)
    
    # get figure factory
    if not fdL and not fdR:
        # ... @todo change?
        ff = LandmarksFigureFactory()
        num_filters = 0
        # ff = CombinedFigureFactory(fdL, color=LEFT_COLOR)
        # num_filters = 1
    elif fdL and not fdR:
        ff = CombinedFigureFactory(fdL, color=LEFT_COLOR)
        num_filters = 1
    elif fdR and not fdL:
        ff = CombinedFigureFactory(fdR, color=RIGHT_COLOR)
        num_filters = 1
    else:
        # both
        ff = ComparisonFigureFactory(fdL, fdR)
        num_filters = 2

    # get view
    viewfunc = determine_view(tab_ids_1, tab_ids_2, num_filters=num_filters)

    # return view
    return dbc.Container(viewfunc(ff), className='viewfunc-container')


def determine_view(tab_ids_1=[], tab_ids_2=[], default=MemberMapView, num_filters=1):
    tab_ids_1_set=set(tab_ids_1)
    if 'data' in tab_ids_1_set:
        return MemberTableView
    elif 'map' in tab_ids_1_set:
        return MemberMapView
    elif 'analysis' in tab_ids_1_set:
        return AnalysisTableView if num_filters>1 else MemberTableView
    
    return default