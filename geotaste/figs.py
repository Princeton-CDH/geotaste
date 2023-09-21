"""
All the classes and functions for drawing figures. These classes do not know about dash components, beyond the `dash_table.DataTable` component returned by `FigureFactory.table`. They rely on the `Dataset` classes in dataset.py and use plotly to plot figures. 

The base class is in `FigureFactory`, which defines the default behavior sufficient for most figures, e.g. `MemberDOBFigure`, etc. There are also `LandmarksFigureFactory`, `CombinedFigureFactory`, and `ComparisonFigureFactory` which contain the code for drawing maps and more complex figures.
"""

from .imports import *


###########
# Figures #
###########

class FigureFactory(DashFigureFactory, Logmaker):
    """
    A class used to represent a factory for generating figures.

    Attributes
    ----------
    records_name : str
        A string indicating the name of the records (default is 'records')
    key : str
        A string to be used as a key to access elements in a record.
    records_points_dim : str 
        A string indicating the dimensionality of the records points (default is 'xy')
    dataset_class : class
        The class of the dataset to be used by the factory (default is Combined)
    drop_duplicates : tuple
        A tuple defining the criteria for dropping duplicate records (default is an empty tuple)
    quant : bool
        A boolean indicating whether or not to perform quantization (default is False)
    opts_xaxis : dict
        A dictionary of options for x-axis (default is an empty dict)
    opts_yaxis : dict
        A dictionary of options for y-axis (default is an empty dict)
    height : int
        An integer indicating the height of the figure (default is 100)
    min_series_val : object
        Minimum value for the series of data (default is None)
    max_series_val : object
        Maximum value for the series of data (default is None)
    color: object
        The color used for the figure (default is None)
    keep_missing_types : bool
        A boolean indicating whether to keep missing types in the data (default is True)
    vertical : bool
        A boolean indicating whether to plot vertical bars (default is False)
    log_x : bool
        A boolean indicating whether to use log scale on x-axis (default is False)
    log_y : bool
        A boolean indicating whether to use log scale on y-axis (default is False)
    text : str
        Key in data frame to be displayed on the graph.
    cols_table : list
        Columns to be shown in self.table()
    """

    records_name = 'records'
    key = ''
    records_points_dim = 'xy'
    dataset_class = Combined
    dataset_obj = None
    drop_duplicates = ()
    quant = False
    opts_xaxis=dict()
    opts_yaxis=dict()
    height=100
    min_series_val=None
    max_series_val=None
    color=None 
    keep_missing_types=True
    vertical=False
    log_x=False
    log_y=False
    text=None
    cols_table=[]
    
    def __init__(self, filter_data={}, selected=[], name='FigureFactory', **kwargs):
        """Initializes an instance of the FigureFactory class.
        
        Args:
            filter_data (dict, optional): A dictionary containing filter data. Defaults to an empty dictionary.
            selected (list or dict, optional): A list or dictionary containing selected data. Defaults to an empty list.
            name (str, optional): The name of the FigureFactory instance. Defaults to 'FigureFactory'.
            **kwargs: Additional keyword arguments that can be used to set attributes of the FigureFactory instance.
        """
        self.name=name
        if filter_data is None: filter_data = {}
        self.filter_data = filter_data
        self.kwargs=kwargs
        for k,v in kwargs.items(): setattr(self,k,v)

        self.selection_data = (
            selected 
            if type(selected) is dict
            else (
                {self.key:selected}
                if self.key
                else {}
            ) 
        )
        

    def has_selected(self):
        """Check if there is any selected data.
        
        Returns:
            bool: True if there is selected data, False otherwise.
        """
        
        return bool(self.selection_data.get(self.key) and self.selected_indices)

    def get_selected(self, selectedData={}):
        """The `get_selected` function returns a dictionary containing selected records based on the provided `selectedData` parameter. If `selectedData` is empty or not provided, an empty dictionary is returned.
        
        Args:
            selectedData (dict): A dictionary containing selected data. Default is an empty dictionary.
        
        Returns:
        - dict: A dictionary with one key, `self.key`, and one value, the selected values [val1, val2, ...]
        """
        return {self.key:get_selected_records_from_figure_selected_data(selectedData, quant=self.quant)}    

    @cached_property
    def dataset(self):
        """Returns the dataset if the dataset class is defined, otherwise returns None.
        
        Returns:
            object: The dataset object if the dataset class is defined, otherwise None.
        """
        if self.dataset_obj is not None: return self.dataset_obj
        if self.dataset_class is None: return None
        if hasattr(self.dataset_class,'__func__'): return self.dataset_class.__func__()
        return self.dataset_class()

    @cached_property
    def data_orig(self):
        """Returns the original data frame from the dataset class instance.

        Returns:
            pandas.DataFrame: The original data from the dataset.
        """

        return (
            self.dataset.data 
            if self.dataset is not None and self.dataset.data is not None
            else pd.DataFrame()
        )
    
    
    @cached_property
    def data(self):
        """Returns a filtered dataframe based on the original data and filter criteria.
        
        Returns:
            pandas.DataFrame: The filtered dataframe.
        """
        
        # query
        odf = filter_df(self.data_orig, self.filter_data, return_query=False)

        # drop down to correct size
        if self.drop_duplicates and len(odf):
            odf=odf.drop_duplicates(self.drop_duplicates)

        return odf
    
    @cached_property
    def filter_desc(self):
        """Filters the description based on the filter data.

        Returns:
            str: The filtered query string, in human-readable format.
        """
        
        return filter_query_str(self.filter_data,human=True)
    
    def get_unique_vals(
            self, 
            sort_by_count=True, 
            series_orig=True, 
            **kwargs): 
        """Return a pandas Series containing unique values from the specified series.
        
        Args:
            sort_by_count (bool, optional): If True, sort the unique values by their count in descending order. 
                If False, sort the unique values in ascending order. Defaults to True.
            series_orig (bool, optional): If True, use the original series for counting. 
                If False, use the deduplicated and filtered series. Defaults to True.
            **kwargs: Additional keyword arguments to be passed to the `get_series` method.
        
        Returns:
            pd.Series: A pandas Series containing the unique values.
        """

        l = list(self.get_series(**kwargs).unique())
        if not sort_by_count:
            l.sort(key=lambda x: x)
        else:
            if series_orig:
                # logger.debug('using original series')
                series = self.series_orig
            else:
                # logger.debug('using dedup\'d and filtered')
                series = self.series
            counts = series.value_counts()
            l.sort(key=lambda x: -counts.loc[x])
        return pd.Series(l, name=self.key)



    @cached_property
    def series(self): 
        """Returns the series from the given dataframe, stored under column `self.key`.
        
        Returns:
            pandas.Series: The series extracted from the dataframe.
        """
        return self.get_series(df=self.data)
    
    @cached_property
    def series_orig(self): 
        """Returns the series from the original unfiltered dataframe, stored under column `self.key`.
        
        Returns:
            pandas.Series: The series extracted from the dataframe.
        """
        
        return self.get_series(df=self.data_orig)

    
    @cached_property
    def series_q(self): 
        """Returns the series from the given dataframe, stored under column `self.key`, in forced quantitative mode.
        
        Returns:
            pandas.Series: The series extracted from the dataframe.
        """
        return self.get_series(df=self.data, quant=True)
    
    @cached_property
    def series_all(self): 
        """Returns the series from the original unfiltered dataframe, stored under column `self.key`.
        
        Returns:
            pandas.Series: The series extracted from the dataframe.
        """
        return self.get_series(df=self.data_orig)
    
    @cached_property
    def series_all_q(self): 
        """Returns the series from the original unfiltered dataframe, stored under column `self.key`, in forced quantitative mode.
        
        Returns:
            pandas.Series: The series extracted from the dataframe.
        """
        return self.get_series(df=self.data_orig, quant=True)
    
    def get_series(self, key:str=None, df:pd.DataFrame=None, quant:bool=None):
        """Get a series from a DataFrame.
        
        Args:
            key (str, optional): The column name of the series. If not provided, the default key will be used.
            df (pd.DataFrame, optional): The DataFrame from which to extract the series. If not provided, the default DataFrame (`self.data`) will be used.
            quant (bool, optional): Whether to apply quantization to the series. If not provided, the default quantization value will be used.
        
        Returns:
            pd.Series: The extracted series.        
        """
        
        if key is None: key=self.key
        if not key: 
            return pd.Series(name=key)
        if df is None: df=self.data
        if not len(df) or not key in set(df.columns): 
            return pd.Series(name=key)
        s=pd.Series(
            qualquant_series(
                flatten_series(df[key]),
                quant=quant if quant is not None else self.quant
            ),
            name=self.key
        ).replace({'':UNKNOWN})
        if self.min_series_val is not None: s=s[s>=self.min_series_val]
        if self.max_series_val is not None: s=s[s<=self.max_series_val]
        return s
    
        
    @cached_property
    def minval(self): 
        """Returns the minimum value in the series.
        
        Returns:
            object: The minimum value in the series.
        """
        
        return self.series.min() if len(self.series) else None
    
    @cached_property
    def maxval(self): 
        """Returns the maximum value in the series.
        
        Returns:
            object: The maximum value in the series.
        """
        
        return self.series.max() if len(self.series) else None
    
    @cached_property
    def minval_q(self): 
        """Returns the minimum value in the quant series.
        
        Returns:
            float: The minimum quant value in the series.
        """
        
        return self.series_q.min() if len(self.series_q) else np.nan
    
    @cached_property
    def maxval_q(self): 
        """Returns the maximum value in the quant series.
        
        Returns:
            float: The maximum quant value in the series.
        """
        
        return self.series_q.max() if len(self.series_q) else np.nan

    @cached_property
    def filtered(self): 
        """Check if the filter_data attribute is not empty.
        
        Returns:
            bool: True if filter_data is not empty, False otherwise.
        """
        return bool(self.filter_data)

    @cached_property
    def df_selections(self) -> pd.DataFrame:
        """Filters the DataFrame based on the selection data.
        
            Returns:
                pd.DataFrame: The filtered DataFrame.
        """
        
        if self.selection_data and len(self.df_counts):
            return filter_df(self.df_counts, self.selection_data)
        return pd.DataFrame()
    
    @cached_property
    def selected_indices(self) -> list:
        """Returns a list of selected values from the dataframe.
        
        Returns:
            list: A list of selected values from the dataframe.
        """
        
        return list(self.df_selections.index) if len(self.df_selections) else []
    
    @cached_property
    def df_counts(self):
        """Returns a DataFrame containing the value counts of the series in the filtered dataframe. If `self.keep_missing_types` is True, then value types not present in the filtered dataframe, but present in the original/unfiltered one, will be added to the returned data frame with a count of 0.
        
            Returns:
                DataFrame: A DataFrame with at least two columns: `self.key` and 'count', where 'count' represents the number of instances of the value type in the filterd dataframe `self.data`.
        """
        
        valcounts = self.series.value_counts()
        if self.keep_missing_types:
            valtypes = self.series_all.unique()
            for missing_val in set(valtypes)-set(valcounts.index):
                valcounts[missing_val]=0
        return pd.DataFrame(valcounts).reset_index()






    ## Plotting

    def plot(self, **kwargs):
        """Plots, by default, a histogram via `self.plot_histogram`, and if selections exist, then these aree subsequently applied.
        
        Args:
            **kwargs: Additional keyword arguments to customize the plot. These arguments will be merged with the existing arguments stored in `self.kwargs`.
        
        Returns:
            fig: The resulting plot as a `plotly.graph_objects.Figure` object.
        """
        
        kwargs={**self.kwargs, **kwargs}
        
        fig = self.plot_histogram(**kwargs)
        
        if self.has_selected():
            fig.update_traces(selectedpoints=self.selected_indices)

        return fig
        
    def plot_histogram(self, color=None, **kwargs):
        """Plots a histogram using Plotly.
        
        Args:
            color (str, optional): The color of the bars. If not provided, the default color will be used.
            **kwargs: Additional keyword arguments that can be passed to the `px.bar` function.
        
        Returns:
            fig: The Plotly figure object representing the histogram.
        """
        
        color = color if color else self.color
        category_orders = (
            {self.key:self.df_counts.index} 
            if self.quant is False 
            else None
        )
        
        fig=px.bar(
            self.df_counts,
            x=self.key if not self.vertical else 'count',
            y='count' if not self.vertical else self.key, 
            height=self.height if not self.vertical else len(self.df_counts)*20,
            color_discrete_sequence=[color] if color else None,
            category_orders=category_orders,
            log_x=self.log_x,
            log_y=self.log_y,
            text=self.text,
            template=PLOTLY_TEMPLATE,
            hover_data={self.key:False, 'count':False},
            # **kwargs
        )
        fig.update_traces(textposition = 'auto', textfont_size=14)

        # cats=list(reversed(self.df_counts[self.key].index))        
        cats=list(self.df_counts[self.key].index)
        if self.vertical:
            fig.update_yaxes(categoryorder='array', categoryarray=cats, title_text='', tickangle=0, autorange='reversed')
            fig.update_xaxes(title_text=f'Number of {self.records_name}', visible=False)
        else:
            fig.update_xaxes(categoryorder='array', categoryarray=cats, title_text='')
            fig.update_yaxes(title_text=f'Number of {self.records_name}', visible=False)
        
        fig.update_layout(
            uniformtext_minsize=10,
            clickmode='event+select', 
            dragmode='select',
            selectdirection='h' if not self.vertical else 'v',
            margin={"r":0,"t":0,"l":0,"b":0},
        )
        if self.opts_xaxis: fig.update_xaxes(**self.opts_xaxis)
        if self.opts_yaxis: fig.update_yaxes(**self.opts_yaxis)

        return fig



    ## Tables
    def table(self, cols=[], **kwargs):
        """Generate a dash_table.DataTable table using the provided data and columns.
        
        Args:
            cols (list, optional): A list of column names to include in the table. If not provided, all columns in `self.cols_table` will be included. Defaults to an empty list.
            **kwargs: Additional keyword arguments to pass to the `get_dash_table` function.
        
        Returns:
            dash_table.DataTable: The generated table as a dash table component.
        """
        
        return get_dash_table(
            self.data, 
            cols=self.cols_table if not cols else cols, 
            **kwargs
        )









## Individual figures


## MEMBER FIGURES ################################################################################


class MemberFigure(FigureFactory):
    """
    A class that creates a figure factory for Members.
    """
    records_name='members'
    drop_duplicates=('member',)



class MemberDOBFigure(MemberFigure):
    """
    A child class of MemberFigure that creates a figure based on the member's date of birth.
    """
    key = 'member_dob'
    quant = True

class MembershipYearFigure(MemberFigure):
    """
    A child class of MemberFigure that creates a figure based on the membership year.
    """
    records_name='annual subscriptions'
    key='member_membership'
    quant = True

class MemberGenderFigure(MemberFigure):
    """
    A child class of MemberFigure that creates a figure based on the member's gender.
    """
    key='member_gender'
    quant=False
    vertical = False
    text = 'count'
    



class NationalityFigure(FigureFactory):
    """
    A class that creates a figure factory for nationality.
    """
    records_points_dim='y'
    vertical = True
    log_x = True
    text = 'count'




class MemberNationalityFigure(NationalityFigure, MemberFigure):
    """
    A child class of NationalityFigure and MemberFigure that creates a figure based on nationality.
    """
    records_name='member nationalities'
    key='member_nationalities'

class MemberArrondFigure(MemberFigure):
    """
    A child class of MemberFigure that creates a figure based on 'arrond_id'.
    """

    key='arrond_id'
    quant=False
    vertical = True
    text = 'count'

    @cached_property
    def df_counts(self):
        """
        A method that computes and returns a dataframe of counts after applying validation and sorting.
        
        Returns:
            (DataFrame) A DataFrame sorted by 'arrond_i'.
        """
        odf=super().df_counts
        series = odf[self.key]
        odf=odf[series.apply(is_valid_arrond)]
        odf['arrond_i'] = odf[self.key].apply(int)
        odf=odf.sort_values('arrond_i')
        odf.index = [x+1 for x in range(len(odf))]
        return odf

    














## BOOK FIGURES ################################################################################

class MemberNameFigure(MemberFigure):
    """
    A child class of MemberFigure that creates a figure based on the member's name.
    """
    key = 'member_name'
    drop_duplicates=('member',)


class BookFigure(FigureFactory):
    """
    A child class of FigureFactory that creates figures based on books.
    """
    records_name='books'
    drop_duplicates=('book',)


class BookTitleFigure(BookFigure):
    """
    A child class of BookFigure that creates a figure based on the book's title.
    """
    key = 'book_title'


class BookGenreFigure(BookFigure):
    """
    A child class of BookFigure that creates a figure based on the book's genre.
    """
    key = 'book_genre'
    vertical = True
    text = 'count'


class BookYearFigure(BookFigure):
    """
    A child class of BookFigure that creates a figure based on the book's publication year.
    """
    key = 'book_year'
    quant = True
    min_series_val=1800
    max_series_val=1950





## AUTHOR FIGURES ################################################################################


class AuthorFigure(FigureFactory):
    """
    A child class of FigureFactory that creates figures based on authors.
    """
    records_name='authors'
    drop_duplicates=('author',)


class AuthorGenderFigure(AuthorFigure):
    """
    A child class of AuthorFigure that creates a figure based on the author's gender.
    """
    key='author_gender'
    quant=False
    vertical = False
    text='count'


class AuthorNationalityFigure(NationalityFigure, AuthorFigure):
    """
    A child class of NationalityFigure and AuthorFigure that creates a figure based on the author's nationality.
    """
    key='author_nationalities'
    quant=False


class AuthorDOBFigure(AuthorFigure):
    """
    A child class of AuthorFigure that creates a figure based on the author's date of birth.
    """
    key = 'author_dob'
    quant = True
    min_series_val=1800
    max_series_val=1950


class AuthorNameFigure(AuthorFigure):
    """
    A child class of AuthorFigure that creates a figure based on the author's name.
    """
    key = 'author_name'


class EventFigure(FigureFactory):
    """
    A child class of FigureFactory that creates figures based on events.
    """
    drop_duplicates = ('event',)


class EventYearFigure(EventFigure):
    """
    A child class of EventFigure that creates a figure based on the event's year.
    """
    key = 'event_year'
    quant = True


class EventMonthFigure(EventFigure):
    """
    A child class of EventFigure that creates a figure based on the event's month.
    """
    key = 'event_month'
    quant = True


class EventTypeFigure(EventFigure):
    """
    A child class of EventFigure that creates a figure based on the event's type.
    """
    key = 'event_type'
    quant = False
    vertical = True






## EVENT FIGURES ################################################################################





## CUSTOM FIGURE FACTORIES ################################################################################

class LandmarksFigureFactory(FigureFactory):
    """
    Figure factory for landmarks data. Dataset class is set to LandmarksDataset.
    """
    dataset_class = Landmarks
    cols_table = ['landmark','address','arrond_id','lat','lon']

    def plot_map(self, color='gray', **kwargs):
        """Plot a scattermapbox with landmarks.
        
        Args:
            color (str, optional): The color of the markers. Defaults to 'gray'.
            **kwargs: Additional keyword arguments.
        
        Returns:
            go.Figure: The scattermapbox figure.
        """
        
        figdf = self.data
        if not 'tooltip' in set(figdf.columns): figdf['tooltip']=''
        fig = go.Figure()
        fig.add_trace(
            go.Scattermapbox(
                below='',
                name='Landmarks',
                mode='markers+text',
                lat=figdf['lat'],
                lon=figdf['lon'],
                marker=go.scattermapbox.Marker(
                    color='black',
                    # symbol='square',
                    size=20,
                    # opacity=1
                    opacity=0.4
                ),
                text=figdf['landmark'],
                customdata=figdf['tooltip'],
                hovertemplate='%{customdata}<extra></extra>',
                textfont=dict(
                    size=TEXTFONT_SIZE,
                    family='Louize, Recursive, Tahoma, Verdana, Times New Roman',
                    color='black'
                ),
                textposition='bottom center',
                hoverlabel=dict(
                    font=dict(
                        size=16,
                        family='Louize, Recursive, Tahoma, Verdana, Times New Roman',
                        # color='black'
                    ),
                    bgcolor='white',
                ),
            )
        )

        # fig.update_layout(mapbox_style=self.map_style, mapbox_zoom=14)
        update_fig_mapbox_background(fig)
        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            legend=dict(
                yanchor="bottom",
                y=0.06,
                xanchor="right",
                x=0.99
            ),
            autosize=True
        )
        fig.update_layout(mapbox_accesstoken=mapbox_access_token)
        fig.layout._config = {'responsive':True, 'scrollZoom':True}
        fig.layout.update(showlegend=False)
        return fig




### COMBINED?

class CombinedFigureFactory(FigureFactory):
    """
    FigureFactory corresponding to CombinedDataset.
    """

    dataset_class = Combined
    cols_table_members=[
        'member_name',
        'member_dob',
        'member_dod',
        'member_nationalities',
        'member_gender',
        'dwelling_address',
    ]

    cols_table_books = [
        'author_name',
        'book_title',
        'book_year',
        # 'num_borrows_overall',
        # 'book_url'
    ]
    cols_table = ['member_name','memer_membership','member_dob','member_gender','member_nationalities','arrond_id']
    
    @cached_property
    def df_dwellings(self): 
        """Returns a DataFrame with unique dwellings as the index. This function drops duplicate rows based on the 'dwelling' column and sets the 'dwelling' column as the index of the resulting DataFrame.

        Returns:
            pandas.DataFrame: A dataframe with dwelling as index
        """
        assert 'dwelling' in set(self.data.columns)
        return self.data.drop_duplicates('dwelling').set_index('dwelling')
    
    @cached_property
    def df_members(self): 
        """Returns a DataFrame with unique members as the index. This function drops duplicate rows based on the 'member' column and sets the 'member' column as the index of the resulting DataFrame.

        Returns:
            pandas.DataFrame: A dataframe with member as index
        """
        return self.data.drop_duplicates('member').set_index('member')
    
    
    @cached_property
    def book_filters_exist(self):
        """Check if any book filters are active.
        
        Returns:
            bool: True if any book filters exist, False otherwise.
        """
        return any(
            fn.startswith('book_') or fn.startswith('author_') or fn.startswith('event_') or fn.startswith('author_')
            for fn in self.filter_data
        )

    def table(self, **kwargs):
        """Generate a dash_table.DataTable table using the provided data and columns. Cols will be st to to `self.cols_table_members` if `self.book_filters_exist`; otherwise, both `self.cols_table_members` and `self.cols_table_books` will be used.
        
        Args:
            **kwargs: Additional keyword arguments to pass to the `get_dash_table` function.
        
        Returns:
            dash_table.DataTable: The generated table as a dash table component.
        """
        
        df = self.df_dwellings.reset_index()
        df=df[df.dwelling_address!='']
        
        # if only members filtered...
        if not self.book_filters_exist:
            df = df.drop_duplicates('dwelling')
            cols = self.cols_table_members
        else:
            df = df.drop_duplicates(['dwelling','book'])
            cols = self.cols_table_members+self.cols_table_books
        return get_dash_table(df, cols=cols)

    
    @cached_property
    def arronds(self):
        """Returns a series containing the unique arrondissement IDs from the 'df_dwellings' DataFrame.
        
        Returns:
            pandas.Series: A series containing the unique arrondissement IDs.
        """
        return qualquant_series(self.df_dwellings.arrond_id, quant=False)

    @cached_property
    def valid_arronds(self): 
        """Returns a filtered DataFrame of valid arronds.
        
        This method filters the DataFrame `arronds` by applying the function `is_valid_arrond` to each row. The resulting DataFrame contains only the rows where `is_valid_arrond` returns True.
        
        Returns:
            pandas.DataFrame: A filtered DataFrame of valid arronds.
        """
        
        return self.arronds.loc[lambda v: is_valid_arrond(v)]

    def plot_map(self, color=None, color_text='black', return_trace=False, **kwargs):
        """Plot a map with member dwellings from the currently filtered data.
        
        Args:
            color (str, optional): The color of the markers. Defaults to None.
            color_text (str, optional): The color of the text. Defaults to 'black'.
            return_trace (bool, optional): Whether to return only the trace. Defaults to False.
            **kwargs: Additional keyword arguments to pass to the function.
        
        Returns:
            go.Figure: The figure object with the map.
        """
        
        if not color and self.color: color=self.color
        if not color: color=DEFAULT_COLOR
        figdf = self.df_dwellings.reset_index().fillna('').query('(lat!="") & (lon!="")')
        # figdf['hovertext']=[x[:100] for x in figdf['hover_tooltip']]

        trace = go.Scattermapbox(
            name=f'Member dwelling ({self.name})',
            mode='markers+text',
            lat=figdf['lat'],
            lon=figdf['lon'],
            customdata=figdf['hover_tooltip'],
            hovertemplate='%{customdata}<extra></extra>',
            marker=go.scattermapbox.Marker(
                color=color,
                symbol='circle',
                size=20,
                # size=(figdf['num_borrows'] / 20)+5,
                opacity=0.4
            ),
            text=figdf['member_name'],
            textfont=dict(
                size=TEXTFONT_SIZE,
                color=color_text,
                family='Louize, Recursive, Tahoma, Verdana, Times New Roman'
            ),
            hoverlabel=dict(
                font=dict(
                    size=16,
                    family='Louize, Recursive, Tahoma, Verdana, Times New Roman',
                    # color='black'
                ),
                bgcolor='white',
            ),
            textposition='bottom center',
        )

        if return_trace: return trace


        fig = go.Figure()
        fig.add_trace(trace)
        fig.update_layout(mapbox_accesstoken=mapbox_access_token)
        return fig




class ComparisonFigureFactory(CombinedFigureFactory):
    """
    A figure factory comparing two CombinedFigureFactories.
    """
    cols_table = ['L_or_R','member_name','memer_membership','member_dob','member_gender','member_nationalities','arrond_id']
    indiv_ff = CombinedFigureFactory

    def __init__(self, ff1={}, ff2={}, **kwargs):
        """Initializes the object with two filter dictionaries or strings.
        
        Args:
            ff1 (dict or str): The first filter dictionary. If a list is provided and `ff2` is not specified, it will be unpacked into `ff1` and `ff2`.
            ff2 (dict or str): The second filter dictionary.
            **kwargs: Additional keyword arguments to be passed to the parent class constructor.
        """
        
        super().__init__(**kwargs)

        if is_listy(ff1) and not ff2 and len(ff1)==2:
            ff1,ff2 = ff1

        self.ff1 = self.L = self.indiv_ff(ff1,name='Filter 1') if type(ff1) in {dict,str} else ff1
        self.ff2 = self.R = self.indiv_ff(ff2,name='Filter 2') if type(ff2) in {dict,str} else ff2
    
    
    def compare(self, 
            maxcats=COMPARISON_MAXCATS,
            cols=PREDICT_COLS,
            only_signif=False,
            round=4,
            min_count=PREDICT_MIN_COUNT,
            min_sum=PREDICT_MIN_SUM,
            **kwargs) -> pd.DataFrame:
        """Compare the dataframes of two objects and return a dataframe of distinctive qualitative values. Overwrite any of these constants in ~/geotaste_data/config.json.
        
        Args:
            maxcats (int): The maximum number of categories to consider (i.e. how 'controlled' the vocabulary is). Defaults to COMPARISON_MAXCATS.
            cols (list): The columns to compare. Defaults to PREDICT_COLS.
            only_signif (bool): Whether to return only statistically significant values. Defaults to False.
            round (int): The number of decimal places to round the returned values. Defaults to 4.
            min_count (int): The minimum count of values to consider. Defaults to PREDICT_MIN_COUNT.
            min_sum (int): The minimum sum of values to consider. Defaults to PREDICT_MIN_SUM.
            **kwargs: Additional keyword arguments.
        
        Returns:
            pd.DataFrame: A dataframe of distinctive qualitative values.
        """
        
        return get_distinctive_qual_vals(
            self.L.data,
            self.R.data,
            maxcats=maxcats,
            cols=cols,
            only_signif=only_signif,
            round=round,
            min_count=min_count,
            min_sum=min_sum,
            drop_duplicates={
                'member':['member'],
                'author':['author','event'],
                'book':['book','event'],
                'arrond_id':['arrond_id','member']
            }
        )
    
    def describe_comparison(self, comparison_df=None, **kwargs):
        """Describes the comparison between two dataframes.
        
        Args:
            comparison_df (pandas.DataFrame, optional): The dataframe containing the comparison results as the result of self.compare().
                If not provided, the function will call self.compare(**kwargs) to generate the comparison dataframe.
            **kwargs: Additional keyword arguments to be passed to self.compare() if comparison_df is not provided.
        
        Returns:
            tuple: A tuple containing two lists of descriptions. The first list describes the comparison for group L, and the second list describes the comparison for group R.
        """
        
        return describe_comparison(
            comparison_df
            if comparison_df is not None
            else self.compare(**kwargs)
        )
    
    def table(self, cols=['arrond_id'], **kwargs):
        """Returns the content of a table based on the provided keyword arguments.
        
        Args:
            **kwargs: Additional keyword arguments to be passed to the `table_content` method.
        
        Returns:
            dbc.Container: The content of the table as well as its prefatory description.
        """
        odf = self.compare(cols=cols, **kwargs)
        if not len(odf):
            return dbc.Container('Analysis failed, likely because one or both groups returns no data, or because both groups are identical.')
        
        fig=None
        if 'arrond_id' in set(cols):
            fig = self.plot_oddsratio_map(odf)
        desc_L,desc_R = self.describe_comparison(odf, lim=10)
        summary_row = dbc.Row([
            dbc.Col([
                html.H5([f'10 most distinctive features for Filter 1 (', self.L.filter_desc,')']),
                dcc.Markdown('\n'.join(desc_L))
            ], className='left-color'),

            dbc.Col([
                html.H5([f'10 most distinctive features for Filter 2 (', self.R.filter_desc,')']),
                dcc.Markdown('\n'.join(desc_R))
            ], className='right-color'),
        ])
        
        table_row = dbc.Row(get_dash_table(odf))

        fig_row_l = [] if not fig else [dbc.Row(dcc.Graph(figure=fig))]
        rows = fig_row_l + [summary_row,table_row]
        
        return dbc.Container(rows, className='table_content')

        
        
        

    
    @cached_property
    def df_dwellings(self): 
        """Combines the 'df_dwellings' dataframes from the left and right datasets.
            
        Returns:
            DataFrame: The combined dataframe of 'df_dwellings' from the left and right datasets.
        """
        
        return combine_LR_df(
            self.L.df_dwellings,
            self.R.df_dwellings, 
            colval_L='Filter 1',
            colval_R='Filter 2',
            colval_LR='Both Groups'
        )

    
    @cached_property
    def df_members(self): 
        """Combines the 'df_dwellings' dataframes from the left and right datasets.
            
        Returns:
            DataFrame: The combined dataframe of 'df_dwellings' from the left and right datasets.
        """

        return combine_LR_df(
            self.L.df_members,
            self.R.df_members, 
            colval_L='Filter 1',
            colval_R='Filter 2',
            colval_LR='Both Groups'
        )
    
    def plot_map(self):
        trace1=self.L.plot_map(return_trace=True)
        trace2=self.L.plot_map(return_trace=True)
        fig = go.Figure()
        fig.add_trace(trace1)
        fig.add_trace(trace2)
        return fig    

    def plot_oddsratio_map(self, comparison_df=None, col='odds_ratio_log', **kwargs):
        """Plots an odds ratio map using a choropleth mapbox.
        
        Args:
            comparison_df (pd.DataFrame, optional): DataFrame containing the data for comparison. If not provided, the function will call the `compare` method of the class. Defaults to None.
            col (str, optional): Column name to use for coloring the map. Defaults to 'odds_ratio_log'.
            **kwargs: Additional keyword arguments to pass to the `compare` method if `comparison_df` is not provided.
        
        Returns:
            plotly.graph_objects.Figure: The plotted odds ratio map.
        """
        
        figdf = comparison_df if comparison_df is not None else self.compare(**kwargs)
        figdf=figdf.query('col=="arrond_id"')
        Lcolor = Color(RIGHT_COLOR)
        Rcolor = Color(LEFT_COLOR)
        midpoint = list(Lcolor.range_to(Rcolor, 3))[1]
        midpoint.set_luminance(.95)

        fig_choro = px.choropleth_mapbox(
            figdf,
            geojson=get_geojson_arrondissement(),
            locations='col_val', 
            color=col,
            center=MAP_CENTER,
            zoom=11,
            # hover_data=[],
            hover_data={'col_val':False, col:False},
            color_continuous_scale=[
                Lcolor.hex,
                midpoint.hex,
                Rcolor.hex,
            ],
            opacity=.5,
        )
        fig_choro.update_mapboxes(
            style='light',
            accesstoken=mapbox_access_token,
        )
        
        ofig = fig_choro

        ofig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            legend=dict(
                yanchor="bottom",
                y=0.06,
                xanchor="right",
                x=0.99
            ),
            coloraxis=dict(
                colorbar=dict(
                    orientation='h', 
                    y=.01,
                    lenmode='fraction',
                    len=.5,
                    thickness=10,
                    xanchor='right',
                    x=.99
                )
            )
        )
        return ofig







def get_dash_table(df, cols=[], page_size=5, height_cell=60):
    """Returns a Dash DataTable object with specified parameters.
    
    Args:
        df (pandas.DataFrame): The input DataFrame.
        cols (list, optional): The list of columns to include in the DataTable. If not provided, all columns from the DataFrame will be included. Defaults to [].
        page_size (int, optional): The number of rows to display per page. Defaults to 5.
        height_cell (int, optional): The height of each cell in pixels. Defaults to 60.
    
    Returns:
        dash_table.DataTable: The Dash DataTable object.
    """
    
    cols=list(df.columns) if not cols else [col for col in cols if col in set(df.columns)]
    dff = delist_df(df[cols])
    cols_l = [{'id':col, 'name':col.replace('_',' ').title()} for col in cols]
    return dash_table.DataTable(
        data=dff.to_dict('records'),
        columns=cols_l,
        sort_action="native",
        sort_mode="multi",
        filter_action="native",
        page_action="native",
        # page_action="none",
        export_format='csv',
        page_size=page_size,
        fixed_rows={'headers': True},
        style_cell={
            'minWidth': 95, 'maxWidth': 95, 'width': 95,
        },

        style_data={
            'minHeight': height_cell, 'maxHeight': height_cell, 'height': height_cell,
            'whiteSpace': 'normal',
        },
        style_table={
            'height':400, 
            'overflowY':'auto',
            # 'display':'block',
            # 'flex-didrection':'column',
            # 'flex-grow':1,
            # 'width':'100%',
            # 'border':'1px solid #eeeee'
            # 'padding-bottom':'100px'
        },
    )



def get_empty_fig(height=100, width=250, **layout_kwargs):
    """Create an empty plot figure with specified height and width.
    
    Args:
        height (int, optional): The height of the plot figure. Defaults to 100.
        width (int, optional): The width of the plot figure. Defaults to 250.
        **layout_kwargs: Additional keyword arguments to be passed to the layout dictionary.
    
    Returns:
        go.Figure: An empty plot figure with the specified height, width, and layout.
    """
    fig=go.Figure(layout=dict(height=height, width=width, **layout_kwargs))
    fig.update_layout(showlegend=False, template='simple_white')
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig






@cache_obj.memoize()
def plot_cache(figure_class, serialized_data=''):
    """Plots the FIGURE using the specified figure class and serialized data. This function output is memoized so that future calls with the same arguments return cached results. This cache is stored in `PATH_CACHE` constant/config flag.
    
    Args:
        figure_class (class): The figure class to use for plotting.
        serialized_data (str): The serialized data to be used for plotting, which should be unpackable to (filter_data,selected,kwargs). If `serialized_data` is empty, an empty filter data, None for selected, and an empty dictionary for kwargs will be used.
    
    Returns:
        str: The zlib-compressed and base64 encoded JSON string representation of the plotted figure.
    """
    
    logger.debug(f'plot_cache({figure_class}, {serialized_data})')
    filter_data,selected,kwargs = (
        unserialize(serialized_data) 
        if serialized_data 
        else ({},None,{})
    )
    ff = figure_class(filter_data=filter_data, selected=selected)
    fig = ff.plot(**kwargs)
    return to_json_gz_str(fig)



def get_ff_for_num_filters(fdL={}, fdR={}, **kwargs):
    """Returns a figure factory based on the number of filters provided.
    
    Args:
        fdL (dict): A dictionary representing the left filter.
        fdR (dict): A dictionary representing the right filter.
        **kwargs: Additional keyword arguments to be passed to the figure factory constructors.
    
    Returns:
        FigureFactory: A figure factory object based on the number of filters provided.
    
    Examples:
        # Example 1: No filters provided
        ff = get_ff_for_num_filters()
        # Returns a LandmarksFigureFactory object
    
        # Example 2: Only left filter provided
        fdL = {'filter_param': 'value'}
        ff = get_ff_for_num_filters(fdL=fdL)
        # Returns a CombinedFigureFactory object with the left filter
    
        # Example 3: Only right filter provided
        fdR = {'filter_param': 'value'}
        ff = get_ff_for_num_filters(fdR=fdR)
        # Returns a CombinedFigureFactory object with the right filter
    
        # Example 4: Both left and right filters provided
        fdL = {'filter_param': 'value'}
        fdR = {'filter_param': 'value'}
        ff = get_ff_for_num_filters(fdL=fdL, fdR=fdR)
        # Returns a ComparisonFigureFactory object
    """
    

    # get figure factory
    num_filters = len([x for x in [fdL,fdR] if x])
    # 3 cases
    if num_filters==0:
        ff = LandmarksFigureFactory(**kwargs)

    elif num_filters==1:
        if fdL:
            ff = CombinedFigureFactory(fdL, color=LEFT_COLOR, **kwargs)
        elif fdR:
            ff = CombinedFigureFactory(fdR, color=RIGHT_COLOR, **kwargs)

    elif num_filters == 2:
        ff = ComparisonFigureFactory(fdL, fdR, **kwargs)

    return ff



@cache_obj.memoize()
def get_cached_fig_or_table(args_id):
    """Produce or retrieve memoized/cached figure or table based on the given serialized arguments 
    
    Args:
        args_id (str): The serialized arguments. These should unpack to (fdL,fdR,active_tab,analysis_tab).
    
    Returns:
        str: The JSON, zlib-compressed string representation of the figure or table.
    """
    
    fdL,fdR,active_tab,analysis_tab=unserialize(args_id)
    ff=get_ff_for_num_filters(fdL,fdR)
    logger.debug([args_id,ff])
    if active_tab=='map':
        out=ff.plot_map()
    else:
        if isinstance(ff,ComparisonFigureFactory):    
            pcols=[c for c in PREDICT_COLS if c.startswith(analysis_tab)] if analysis_tab else PREDICT_COLS
            out=ff.table(cols=pcols)
        else:
            out=ff.table()
    return to_json_gz_str(out)

def to_json_gz_str(out):
    """Converts the given object to a JSON string, compresses it using zlib, and returns the compressed string.
    
    Args:
        out: The object to be converted to JSON.
    
    Returns:
        str: The compressed JSON string.
    """
    
    ojson=pio.to_json(out)
    ojsongz=b64encode(zlib.compress(ojson.encode()))
    ojsongzstr=ojsongz.decode('utf-8')
    return ojsongzstr

def from_json_gz_str(ojsongzstr):
    """
    This function takes a base64 encoded zlib compressed JSON string as input and
    decompresses and decodes it back to the original JSON format.

    Args:
        ojsongzstr (str): The input string which is a base64 encoded and zlib compressed JSON string.

    Returns:
        object: The original JSON object obtained after decompressing and decoding the input string.
    """
    ojsongz=b64decode(ojsongzstr.encode())
    ojson=zlib.decompress(ojsongz)
    try:
        return pio.from_json(ojson)
    except ValueError:
        return orjson.loads(ojson)




def update_fig_mapbox_background(fig):
    """Updates the background of a Mapbox figure.
    
    Args:
        fig (plotly.graph_objs._figure.Figure): The figure to update.
    
    Returns:
        plotly.graph_objs._figure.Figure: The updated figure.
    """
    
    fig.update_mapboxes(
        # style='mapbox://styles/ryanheuser/cljef7th1000801qu6018gbx8',
        # style='stamen-toner',
        style="streets",
        layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "paris1937",
                "source": BASEMAP_SOURCES,
            }
        ],
        # style='mapbox://styles/ryanheuser/cllpenazf00ei01qi7c888uug',
        accesstoken=mapbox_access_token,
        bearing=0,
        center=MAP_CENTER,
        pitch=0,

        zoom=14,
    )
    return fig





def get_selected_records_from_figure_selected_data(selectedData:dict={}, quant=None):
    """Get selected records from figure selected data.
    
    Args:
        selectedData (dict, optional): The selected data from the figure. Defaults to {}.
    
    Returns:
        list: The selected records.
    
    Examples:
        >>> selectedData = {'points': [{'label': 'A', 'location': 'NY'}, {'label': 'B', 'location': 'LA'}]}
        >>> get_selected_records_from_figure_selected_data(selectedData)
        ['A', 'B']
    """
    
    if not selectedData: return {}
    
    points_data = selectedData.get('points',[])
    if not points_data: return {}

    def get_record_id(d, keys=['label', 'location']):
        """
        Find the right kind of record label for the given plotly data type
        """
        if not d: return None
        for k in keys:
            if k in d:
                return d[k]
        logger.exception('What is the record id here? --> '+pformat(d))
    
    selected_records = qualquant_series(
        [x for x in [ get_record_id(d) for d in points_data ] if x], 
        quant=quant
    ).sort_values().tolist()
    return selected_records