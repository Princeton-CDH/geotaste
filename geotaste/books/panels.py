from ..imports import *
from .components import *

class BookPanel(FilterPanel, FilterCard):
    desc = 'Book filters'
    records_name='books'
    
    @cached_property
    def year_card(self): return BookYearCard(**self._kwargs)
    @cached_property
    def title_card(self): return BookTitleCard(**self._kwargs)
    @cached_property
    def creator_card(self): return BookCreatorCard(**self._kwargs)
    @cached_property
    def creator_gender_card(self): return CreatorGenderCard(**self._kwargs)
    
    @cached_property
    def subcomponents(self):
        return [self.creator_card, self.title_card, self.year_card, self.creator_gender_card]
