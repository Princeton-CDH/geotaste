from .imports import *

def filter_query_str_series(sname,svals, op='or', maxlen=2,plural_cols=None,fname='overlaps'):
    """
    Filters a query string series based on the given parameters.

    Args:
        sname (str): The name of the query string series.
        svals (list): The values of the query string series.
        op (str, optional): The operator to use for combining multiple values. Defaults to 'or'.
        maxlen (int, optional): The maximum length of svals before using the fname function. Defaults to 2.
        plural_cols (list, optional): The list of plural column names. Defaults to None.
        fname (str, optional): The name of the function to use when sname is in plural_cols. Defaults to 'overlaps'.

    Returns:
        str: The filtered query string series.

    Examples:
        >>> filter_query_str_series('name', ['John', 'Jane', 'Alice'], maxlen=3, op='or')
        '(name==\'John\') or (name==\'Jane\') or (name==\'Alice\')'

        >>> filter_query_str_series('age', [18, 19, 20])
        '(age==18) and (age==19) and (age==20)'

        >>> filter_query_str_series('score', [80, 90, 100], maxlen=3, plural_cols=['score'])
        '@overlaps(score,[80, 90, 100])'
    """
    
    if (plural_cols is not None and sname in set(plural_cols)):
        return f'@{fname}({sname},{svals})'
    
    elif is_range_of_ints(svals):
        return f'{svals[0]} <= {sname} <= {svals[-1]}'

    elif len(svals) > maxlen:
        return f'@{fname}({sname},{svals})'

    else:
        o = f' {op} '.join(f'({sname}=={repr(x)})' for x in svals)
        return f'({o})' if len(svals)>1 else o

def filter_query_str(filter_data:dict, test_func:'function'=overlaps, operator:str='and', plural_cols:list|None=None, multiline:bool=False) -> str:
    """Filter a query string based on the given filter data.

    Args:
        filter_data (dict): A dictionary containing the filter data. The keys represent the column names, and the values represent the filter values.
        test_func (function or str, optional): The function or name of the function to use for testing the filter values. Defaults to overlaps.
        operator (str, optional): The operator to use for combining multiple filter conditions. Defaults to 'and'.
        plural_cols (list, optional): A list of column names that should be treated as plural. Defaults to None.
    
    Returns:
        str: The filtered query string.
    
    Example:
        >>> filter_data = {'name': ['John', 'Jane'], 'age': [25, 30]}
        >>> filter_query_str(filter_data)
        "(name=='John' or name=='Jane') and (age==25 or age==30)"
    """
    
    if not filter_data: return ''
    fname=test_func.__name__ if type(test_func)!=str else test_func
    
    return f' {operator} '.join([
        format_series(sname,svals)
        for sname,svals in filter_data.items()
        if svals is not None
    ])

def filter_df(df:pd.DataFrame, filter_data={}, test_func:'function'=overlaps, operator:str='and', plural_cols:list|None=None, return_query:bool=False) -> pd.DataFrame:
    """Filter a pandas DataFrame based on the provided filter data.

    Args:
        df (pd.DataFrame): The DataFrame to be filtered.
        filter_data (dict, optional): The filter data to be applied. Defaults to an empty dictionary.
        test_func (function, optional): The function used to test the filter conditions. Defaults to overlaps.
        operator (str, optional): The operator used to combine multiple filter conditions. Defaults to 'and'.
        plural_cols (list or None, optional): The list of columns that contain lists. Defaults to None.
        return_query (bool, optional): Whether to return the filter query string along with the filtered DataFrame. Defaults to False.

    Returns:
        pd.DataFrame or tuple: The filtered DataFrame or a tuple containing the filter query string and the original DataFrame.
    """
    
    # determine which cols are plural (have lists in them)
    if plural_cols is None: plural_cols = find_plural_cols(df)
        
    # get query string
    qstr=filter_query_str(
        filter_data,
        test_func=test_func,
        operator=operator, 
        plural_cols=plural_cols
    )

    # query and return
    odf=df.query(qstr) if qstr else df
    return (qstr,df) if return_query else odf

def filter_series(series:pd.Series, vals:list = [], test_func:'function' = isin_or_hasone, matches:list=[]) -> pd.Series:
    """
    Filter a pandas Series based on specified values or a custom test function.

    Args:
        series (pd.Series): The pandas Series to be filtered.
        vals (list, optional): A list of values to filter the Series by. Defaults to an empty list.
        test_func (function, optional): A custom test function to filter the Series by. Defaults to isin_or_hasone.
        matches (list, optional): A list of index labels to filter the Series by. Defaults to an empty list.

    Returns:
        pd.Series: The filtered pandas Series.
    """
    if matches: series_matching = series[[m for m in matches if m in set(series.index)]]
    elif not vals: series_matching = series
    else: series_matching = series[series.apply(lambda x: test_func(x, vals))]    
    return series_matching
