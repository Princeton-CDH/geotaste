from ..imports import *
from .datasets import *
from ..app.figs import FigureFactory

class BooksFigure(FigureFactory):
    records_name='books'
    dataset_class = BooksDataset
    
    @cached_property
    def figdf(self):
        if not len(self.df): return pd.DataFrame()
        iname = self.df.index.name
        return pd.DataFrame([
            {iname:i, self.key:v}
            for i,vals in zip(self.df.index, self.df[self.key])
            for v in flatten_list(vals)
        ]).sort_values([self.key, iname]).set_index(iname)

class BookTitleFigure(BooksFigure):
    key='title'

class BookYearFigure(BooksFigure):
    key='year'
    records_points_dim = 'x'

    def plot(self, color=None, min_year=1835, max_year=1945, **kwargs):
        # s = self.series[self.series.apply(lambda x: min_year<=x<=max_year)]
        fig = super().plot_histogram_bar(self.key, color=color)
        fig.update_xaxes(range=[min_year, max_year], title_text='')
        fig.update_yaxes(visible=False)
        return fig
