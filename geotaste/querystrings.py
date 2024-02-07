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
        fname='contains',
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
            format_query_pandas(sname,svals,groupby,fname=fname) 
            if not human else
            format_query_human(sname,svals)
        )
        for sname,svals in filter_data.items()
        if svals
    ])
    return query

def format_query_pandas(sname, svals, groupby:Optional[str]=None,fname='contains'):
    """
    Generates a pandas-compatible query string.
    """
    if to_set(svals) == {'*'} or to_set(svals) == {'~'}:
        return format_boolean_query_pandas(
            sname,
            groupby,
            is_neg='~' in to_set(svals)
        )

    # make sure input is listlike
    svals, is_neg = preprocess_for_possible_opening_negation(svals)
    fname = get_query_func(groupby, is_neg)

    if groupby:
        return f'@{fname}({groupby}, {sname}, {format_query_vals(svals)})'
    else:
        return f'@{fname}({sname}, {format_query_vals(svals)})'

        

def get_query_func(groupby, is_neg):
    if not groupby:
        if not is_neg:
            return 'contains'
        else:
            return 'contains_other'
    else:
        if not is_neg:
            return 'group_contains'
        else:
            return 'group_never_contains'



def format_query_vals(x):
    return json.dumps(x, ensure_ascii=False)

def format_boolean_query_pandas(
        sname, 
        groupby:Optional[str]=None,
        is_neg=False,
        fname='has_any_value',
    ):
    posneg = '~' if is_neg else ''
    if groupby:
        return f'{posneg}@group_{fname}({groupby}, {sname})'
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

