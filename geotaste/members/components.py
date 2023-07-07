from ..imports import *
from ..app.components import *
from ..combined.datasets import CombinedDataset
from .figs import *


class MemberInputCard(FilterInputCard):
    dataset_class = CombinedDataset

class MemberNameCard(MemberInputCard):
    desc = 'Filter by member name'
    key='member_sort_name'
    placeholder='Select individual members'

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
