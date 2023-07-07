from ..imports import *
from .components import *

class MemberPanel(FilterPlotPanel, FilterCard):
    desc = 'Member filters'
    records_name='members'

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
    def arrond_card(self): return MemberArrondCard(**self._kwargs)

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
    