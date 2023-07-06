from ..imports import *
from .figs import *
from ..app.components import FilterPlotCard, FilterCard

class BookYearCard(FilterPlotCard):
    desc = 'Date of book\'s publication'
    key='year'
    figure_factory = BookYearFigure

