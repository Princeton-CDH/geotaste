from .imports import *

def format_query_human(sname, svals):
    """
    Generates a human-readable query string.
    """
    # make sure input is listlike
    svals, is_neg = preprocess_for_possible_opening_negation(svals)

    def repr(x): return json.dumps(x, ensure_ascii=False)

    if len(svals) == 1:
        return f'{humancol(sname)} is {"not " if is_neg else ""}{repr(svals[0])}'
    elif int in {type(svx) for svx in svals}:
        return f'{humancol(sname)} {"does not " if is_neg else ""} range{"s" if is_neg else ""} from {svals[0]} through {svals[-1]}'
    else:
        return f'{humancol(sname)} is {"n" if is_neg else ""}either {oxfordcomma(svals, repr=repr, op="or" if not is_neg else "nor")}'


def format_query(
        filter_data:dict, 
        groupby:Optional[str]=None,
        operator:str='and',
        human:bool = False) -> str:
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
    sep = f' {operator} '
    query=sep.join([
        (
            format_query_pandas(sname,svals,groupby) 
            if not human else
            format_query_human(sname,svals)
        )
        for sname,svals in filter_data.items()
        if svals
    ])
    return query




def filter_df(df:pd.DataFrame, filter_data={}, groupby:Optional[str]=None, fname:str='overlaps', fname_group:str='group_overlaps', operator:str='and', plural_cols:list=None, return_query:bool=False) -> pd.DataFrame:
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
    # if plural_cols is None: plural_cols = find_plural_cols(df)
        
    # get query string
    qstr=format_query(
        filter_data,
        groupby=groupby,
        operator=operator, 
        human=False,
    ) if type(filter_data)!=str else filter_data

    # query and return
    if qstr: logger.debug(f'Querying: {qstr}')
    odf=df.query(qstr) if qstr else df
    return (qstr,odf) if return_query else odf



def format_query_vals(x):
    return json.dumps(x, ensure_ascii=False)

def format_boolean_query_pandas(
        sname, 
        groupby:Optional[str]=None,
        is_neg=False,
        fname='has_any_value_for',
        fname_group:str='group_has_any_value_for'
    ):
    posneg = '~' if is_neg else ''
    if groupby:
        return f'{posneg}@{fname_group}({groupby}, {sname})'
    else:
        return f'{posneg}@{fname}({sname})'

    
    




def format_query_vals(x):
    return json.dumps(x, ensure_ascii=False)

def format_boolean_query_pandas(
        sname, 
        groupby:Optional[str]=None,
        is_neg=False,
        fname='has_any_value_for',
        fname_group:str='group_has_any_value_for'
    ):
    posneg = '~' if is_neg else ''
    if groupby:
        return f'{posneg}@{fname_group}({groupby}, {sname})'
    else:
        return f'{posneg}@{fname}({sname})'

    
    
def preprocess_for_possible_opening_negation(svals, symbol='~'):
    """
    Preprocesses the input values to handle negation and ensure list-like input.
    """
    if not svals: return svals
    
    # Ensure svals is list-like
    if not is_listy(svals): 
        if type(svals) is str and svals[0]==symbol:
            is_neg=True
            svals = [svals[1:]]
        else:
            is_neg=False
            svals = [svals]
    elif len(svals)==1:
        return preprocess_for_possible_opening_negation(svals[0], symbol=symbol)
    elif svals[0] == symbol:
        svals = svals[1:]
        is_neg = True
    else:
        is_neg = False

    return svals, is_neg

def format_query_pandas(sname, svals, groupby:Optional[str]=None,fname='overlaps',  fname_group:str='group_overlaps'):
    """
    Generates a pandas-compatible query string.
    """
    if to_set(svals) & {'*','~'}:
        return format_boolean_query_pandas(
            sname,
            groupby,
            is_neg='~' in to_set(svals)
        )

    # make sure input is listlike
    svals, is_neg = preprocess_for_possible_opening_negation(svals)

    posneg='~' if is_neg else ''
    if not groupby:
        return f'{posneg}@{fname}({sname}, {format_query_vals(svals)})'
    else:
        return f'{posneg}@{fname_group}({groupby}, {sname}, {format_query_vals(svals)})'





def overlaps(series: pd.Series, matching: Union[Iterable,str,int], allow_none=False) -> pd.Series:
    """Checks if any element in the given series overlaps with the values in
    the given list.

    Args:
        series (pandas.Series): The series to check for overlaps.
        vals (list): The list of values to check for overlaps with the series.

    Returns:
        pandas.Series: A boolean series indicating if each element in the series overlaps with any value in the list.
    """
    if is_null(matching): return series
    vals_set = to_set(matching)
    series_set = series.apply(to_set)
    res = series_set.apply(lambda xset: None if not xset else bool(xset & vals_set))
    return res if allow_none else res.apply(bool)


def group_overlaps(groups:pd.Series, series: pd.Series, matching: list, allow_none=False) -> pd.Series:
    if not len(matching): return series
    if groups is None or not len(groups): groups = series.index
    assert len(series) == len(groups)

    matching,is_neg = preprocess_for_possible_opening_negation(matching)

    minidf = pd.DataFrame({'grp':groups, 'val':series})
    def get_grp_truth(series):
        overlapping_by_row = no_null_series(overlaps(series,matching,allow_none=True))
        valtypes = set(overlapping_by_row)
        return False in valtypes if is_neg else True in valtypes
    group_to_truth = {
        grpname:get_grp_truth(grpdf.val)
        for grpname,grpdf in minidf.groupby('grp')
    }
    res = pd.Series(
        (group_to_truth[g] for g in groups), 
        index=series.index, 
        name=series.name
    )
    return res if allow_none else res.apply(bool)


def has_any_value_for(series):
    return series.apply(is_not_null)


def group_has_any_value_for(groups, series):
    minidf = pd.DataFrame({'grp':groups, 'val':series})
    group_to_truth = {
        grpname:any(has_any_value_for(grpdf.val))
        for grpname,grpdf in minidf.groupby('grp')
    }
    return pd.Series(
        (group_to_truth[g] for g in groups), 
        index=series.index, 
        name=series.name
    )




