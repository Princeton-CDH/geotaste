from ..imports import *
from .figs import CombinedFigureFactory

class MetaPanel(FilterPanel):
    
    @cached_property
    def member_panel(self): 
        return MemberPanel(**self._kwargs)
    
    @cached_property
    def book_panel(self): return BookPanel(**self._kwargs)

    @cached_property
    def subcomponents(self):
        return [self.member_panel, self.book_panel]


class CombinedPanel(FilterPlotPanel, FilterCard):
    figure_factory = CombinedFigureFactory
    desc = 'Filters'
    records_name='members'

    @cached_property
    def member_name_card(self): 
        from ..members.components import MemberNameCard
        return MemberNameCard(**self._kwargs)
    
    @cached_property
    def member_dob_card(self): 
        from ..members.components import MemberDOBCard
        return MemberDOBCard(**self._kwargs)
    
    @cached_property
    def membership_year_card(self): 
        from ..members.components import MembershipYearCard
        return MembershipYearCard(**self._kwargs)
    
    @cached_property
    def member_gender_card(self): 
        from ..members.components import MemberGenderCard
        return MemberGenderCard(**self._kwargs)
    
    @cached_property
    def member_nation_card(self): 
        from ..members.components import MemberNationalityCard
        return MemberNationalityCard(**self._kwargs)
    
    @cached_property
    def member_arrond_card(self): 
        from ..members.components import MemberArrondCard
        return MemberArrondCard(**self._kwargs)

    @cached_property
    def subcomponents(self):
        return [
            self.member_name_card,
            self.membership_year_card,
            self.member_dob_card,
            self.member_gender_card,
            self.member_nation_card,
            self.member_arrond_card,
        ]
    