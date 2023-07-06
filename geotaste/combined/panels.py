from ..imports import *

class CombinedPanel(FilterPanel):
    
    @cached_property
    def member_panel(self): 
        return MemberPanel(
            name=self.name+'-Members',
            **self._kwargs
        )
    
    @cached_property
    def book_panel(self): return BookPanel(
            name=self.name+'-Books',
            **self._kwargs
        )

    @cached_property
    def subcomponents(self):
        return [self.member_panel, self.book_panel]

    # def layout(self, params=None):
    #     return dbc.Container(
    #         [
    #             self.member_panel.layout(params), 
    #             self.book_panel.layout(params),
    #             self.store,
    #         ], 
    #         className='combined-panel'
    #     )

    # def component_callbacks(self, app):
    #     super().component_callbacks(app)

    #     @app.callback(
    #         Output(self.store, 'data',allow_duplicate=True),
    #         [ 
    #             Input(self.member_panel.store, 'data'),
    #             Input(self.book_panel.store, 'data'),
    #         ],
    #         prevent_initial_call=True
    #     )
    #     def component_filters_updated(*filters_d):
    #         self.filter_data = intersect_filters(*filters_d)
    #         return self.filter_data
