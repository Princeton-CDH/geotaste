from ..imports import *
from ..app.components import *
from .datasets import *
from .figs import *


class MemberInputCard(FilterInputCard):
    dataset_class = MembersDataset

class MemberNameCard(MemberInputCard):
    desc = 'Filter by member name'
    key='sort_name'

    @cached_property
    def input(self):
        s=Members().data[self.key]
        return dcc.Dropdown(
            options = [dict(value=lbl, label=lbl) for idx,lbl in zip(s.index, s)],
            value = [],
            multi=True,
            placeholder='Select individual members'
        )

class MemberDOBCard(FilterPlotCard):
    desc = 'Filter by date of birth'
    key='birth_year'
    figure_factory = MemberDOBFigure    
    
    
class MembershipYearCard(FilterPlotCard):
    desc = 'Filter by years of membership'
    key='membership_years'
    figure_factory = MembershipYearFigure    

class MemberGenderCard(FilterPlotCard):
    desc = 'Filter by gender of member'
    key='gender'
    figure_factory = MemberGenderFigure

class MemberNationalityCard(FilterPlotCard):
    desc = 'Filter by nationality of member'
    key='nationalities'
    figure_factory = MemberNationalityFigure

    @cached_property
    def graph(self):
        return dcc.Graph(figure=self.plot(), config={'displayModeBar':False})

class MemberArrondCard(FilterPlotCard):
    desc = 'Filter by arrondissement'
    key='arrond_id'
    figure_factory = MemberArrondMap
