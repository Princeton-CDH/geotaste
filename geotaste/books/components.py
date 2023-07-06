from ..imports import *
from .figs import *
from ..app.components import FilterPlotCard, FilterCard



class BookTitleCard(FilterInputCard):
    dataset_class = BooksDataset
    desc = 'Filter by book title'
    key='title'
    multi = True
    placeholder = 'Select books by title'


class BookCreatorCard(FilterInputCard):
    dataset_class = CreationsDataset
    desc = 'Filter by creator'
    key='creator'
    multi = True
    placeholder = 'Select books by creator'
    

class BookYearCard(FilterPlotCard):
    desc = "Date of book's publication"
    key='year'
    figure_factory = BookYearFigure

class CreatorGenderCard(FilterPlotCard):
    desc = 'Filter by gender of creator'
    key='creator_Gender'
    figure_factory = CreatorGenderFigure