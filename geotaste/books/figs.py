from ..imports import *
from .datasets import *
from ..app.figs import DatasetFigure

class BooksFigure(DatasetFigure):
    records_name='books'
    dataset_class = BooksDataset

class CreationsFigure(DatasetFigure):
    records_name='works'
    dataset_class = CreationsDataset
    

class BookYearFigure(BooksFigure):
    key='year'
    records_points_dim = 'x'

    def plot(self, color=None, min_year=1835, max_year=1945, **kwargs):
        # s = self.series[self.series.apply(lambda x: min_year<=x<=max_year)]
        fig = super().plot_histogram_bar(self.key, color=color)
        fig.update_xaxes(range=[min_year, max_year], title_text='')
        fig.update_yaxes(visible=False)
        return fig


class CreatorGenderFigure(CreationsFigure):
    key='creator_Gender'

    def plot(self, color=None, **kwargs):
        fig = super().plot_histogram_bar(
            x=self.key,
            color=color,
            # log_y=True,
            quant=False,
            height=100,
            text='count'
        )
        fig.update_yaxes(visible=False)
        fig.update_xaxes(title_text='')
        return fig


