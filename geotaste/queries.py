from .imports import *

def humancol(col):
    if not '_' in col: return col
    a,b = col.split('_',1)
    b = b.title() if b!='dob' else 'DOB'
    if b == 'Membership': return b
    return a.title() + ' ' + b


def filter_query_str_series(
        sname:str, 
        svals:'Iterable', 
        op:str='or', 
        maxlen=1,
        plural_cols=None,
        fname='overlaps',
        human:bool=False
        ):
    """
    Generates a query string for filtering a series based on a given column name and values.

    Args:
        sname (str): The name of the column to filter on.
        svals (Iterable): The values to filter on.
        op (str, optional): The operator to use for combining multiple values. Defaults to 'or'.
        maxlen (int, optional): The maximum number of values allowed before using a plural representation. Defaults to 1.
        plural_cols (list, optional): A list of column names that should use a plural representation. Defaults to None.
        fname (str, optional): The function name to use in the plural representation. Defaults to 'overlaps'.
        human (bool, optional): Whether to generate a human-readable representation. Defaults to False.

    Returns:
        str: The generated query string.
    """
    
    # make sure input is listlike
    if not is_listy(svals): svals=[svals]

    # is negation?
    if svals and svals[0]=='~':
        svals=[v for v in svals[1:]]
        posneg='~'
        is_neg=True
    else:
        posneg=''  
        is_neg=False

    # stringifying
    def repr(x): return json.dumps(x, ensure_ascii=False)

    def getplural():
        if not human:
            return f'{posneg}@{fname}({sname}, {repr(svals)})'
        else:
            return f'{humancol(sname)} is {"n" if is_neg else ""}either {oxfordcomma(svals, repr=repr, op="or" if not is_neg else "nor")}'
        
    def getrange():
        if not human:
            return f'{posneg}({svals[0]} <= {sname} <= {svals[-1]})'
        else:
            return f'{humancol(sname)} {"does not" if is_neg else ""} range{"s" if not is_neg else ""} from {svals[0]} through {svals[-1]}'
    
    def getsinglequerygroup():
        strs=[
            (
                f'({sname} {"=" if not is_neg else "!"}= {repr(x)})' 
                if not human
                else f'{humancol(sname)} is {"not " if is_neg else ""}{repr(x)}'
            )
            for x in svals
        ]
        o = f' {op} '.join(strs)
        return f'({o})' if len(strs)>1 else o

    # return function if this is a list-containing col
    if (plural_cols is not None and sname in set(plural_cols)):
        return getplural()
    
    # if a range of ints, use a less/greater than syntax
    # elif is_range_of_ints(svals):
    elif int in {type(svx) for svx in svals}:
        return getrange()

    # if simply too many vals
    elif len(svals) > maxlen:
        return getplural()

    # otherwise, compound
    else:
        return getsinglequerygroup()
        

def filter_query_str(filter_data:dict, test_func:'function'=overlaps, maxlen=1, operator:str='and', plural_cols:list=None, human:bool=False) -> str:
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

    # filter_data = {**filter_data}
    # is_negation = '_not' in filter_data and filter_data.pop('_not')
    
    sep = f' {operator} '
    query=sep.join([
        filter_query_str_series(sname,svals,op='or',maxlen=maxlen,plural_cols=plural_cols,fname=fname,human=human)
        for sname,svals in filter_data.items()
        if svals
    ])
    return query# if not is_negation else f'~({query})'

def filter_df(df:pd.DataFrame, filter_data={}, test_func:'function'=overlaps, operator:str='and', plural_cols:list=None, return_query:bool=False) -> pd.DataFrame:
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
    ) if type(filter_data)!=str else filter_data

    # query and return
    if qstr: logger.debug(f'Querying: {qstr}')
    odf=df.query(qstr) if qstr else df
    return (qstr,df) if return_query else odf
