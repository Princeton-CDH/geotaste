from .imports import *


def hasone(x: list, y: list) -> bool:
    """Checks if there is at least one common element between two lists.

    Args:
        x (list): The first list.
        y (list): The second list.

    Returns:
        bool: True if there is at least one common element between the two lists, False otherwise.
    """
    res = bool(set(x) & set(y))
    return res


def isin(x: object, y: list) -> bool:
    """Checks if an object is present in a given list.

    Args:
        x (object): The object to be checked.
        y (list): The list in which the object is checked.

    Returns:
        bool: True if the object is present in the list, False otherwise.
    """
    res = bool(x in set(y))
    return res


def isin_or_hasone(x: object, y: list) -> bool:
    """Check if an object is in a list or has at least one element in a list.

    Args:
        x (object): The object to check.
        y (list): The list to check against.

    Returns:
        bool: True if the object is in the list or has at least one element in the list, False otherwise.
    """

    if not is_listy(y):
        y = {y}
    else:
        y = set(y)
    if type(x) in {list, set, tuple}:
        return hasone(x, y)
    else:
        return isin(x, y)


def to_set(x: object) -> set:
    """Converts a value to a set.

    Args:
        x: The value to be converted.

    Returns:
        A set containing the value `x` if `x` is not a list-like object, otherwise a set containing all the elements of `x`.
    """
    return {x} if not is_listy(x) else set(flatten_list(x))


# def is_negation(number_or_str):
#     # if isinstance(number_or_str,Number):
#     #     return number_or_str<0
#     # else:
#     #     return number_or_str.startswith('-')

# def de_negate(number_or_str):
#     if is_negation(number_or_str):
#         return number_or_str*-1 if isinstance(number_or_str,Number) else number_or_str[1:]
#     else:
#         return number_or_str


def overlaps(series: pd.Series, vals: list) -> pd.Series:
    """Checks if any element in the given series overlaps with the values in
    the given list.

    Args:
        series (pandas.Series): The series to check for overlaps.
        vals (list): The list of values to check for overlaps with the series.

    Returns:
        pandas.Series: A boolean series indicating if each element in the series overlaps with any value in the list.
    """
    if not vals: return series
    vals_set = to_set(vals)
    series_set = series.apply(to_set)
    res = series_set.apply(lambda xset: bool(xset & vals_set))
    return res


def is_numeric(x: object) -> bool:
    """Checks if the given object is a numeric value.

    Args:
        x (object): The object to be checked.

    Returns:
        bool: True if the object is a numeric value, False otherwise.
    """
    return isinstance(x, numbers.Number)


def is_listy(x: object) -> bool:
    """Checks if the input object is a list-like object.

    Args:
        x (object): The object to be checked.

    Returns:
        bool: True if the object is a tuple, list, or pandas Series; False otherwise.
    """
    return type(x) in {tuple, list, pd.Series}


def as_int_if_poss(x: Number) -> int:
    return ensure_int(x, return_orig=True)


def ensure_int(x: Number, return_orig=True, default=None) -> int:
    try:
        return int(x)
    except (ValueError, TypeError):
        return (x if return_orig else default)


def ensure_dict(x: object) -> dict:
    """Ensures that the input is a dictionary.

    Args:
        x (object): The input object to be checked.
    
    Returns:
        dict: The input object as a dictionary, or an empty dictionary if the input is None.
    
    Examples:
        >>> ensure_dict(None)
        {}
        
        >>> ensure_dict({'a': 1, 'b': 2})
        {'a': 1, 'b': 2}
        
        >>> ensure_dict([('a', 1), ('b', 2)])
        {'a': 1, 'b': 2}
    """
    if x is None: return {}
    if type(x) is dict: return x
    return dict(x)


def find_plural_cols(df: pd.DataFrame) -> list:
    """Finds the columns in a pandas DataFrame that contain lists.

    Args:
        df (pandas.DataFrame): The DataFrame to search for columns with lists.

    Returns:
        list: A list of column names that contain lists.
    """
    return list(df.columns[(df.applymap(type) == list).any()])


def first(l: Iterable, default: object = None) -> object:
    """Returns the first element of an iterable object.

    Args:
        l (Iterable): The iterable object, e.g. a list.
        default (object, optional): The default value to return if the iterable is empty. Defaults to None.

    Returns:
        object: The first element of the iterable, or the default value if the iterable is empty.
    """
    for x in l:
        return x
    return default


def flatten_list(s: Iterable) -> list:
    """Flattens a nested list into a single list.

    Args:
        s (Iterable): The input iterable containing nested lists.
    
    Returns:
        list: A flattened list containing all elements from the input iterable.
    
    Examples:
        >>> flatten_list([1, 2, [3, 4], [5, [6, 7]]])
        [1, 2, 3, 4, 5, 6, 7]
    
        >>> flatten_list([[1, 2], [3, 4], [5, 6]])
        [1, 2, 3, 4, 5, 6]
    
        >>> flatten_list([1, [2, [3, [4, [5]]]]])
        [1, 2, 3, 4, 5]
    """
    l = []
    for x in s:
        if is_listy(x):
            l += flatten_list(x)
        else:
            l += [x]
    return l


def flatten_series(s: pd.Series) -> pd.Series:
    """Flattens a pandas Series object by converting any nested lists into
    individual elements.

    Args:
        s (pd.Series): The pandas Series object to be flattened.
    
    Returns:
        pd.Series: The flattened pandas Series object.
    
    Example:
        >>> s = pd.Series([1, [2, 3], 4])
        >>> flatten_series(s)
        0    1
        1    2
        2    3
        3    4
        dtype: object
    """
    iname = s.name
    s = pd.Series(s)
    l = []
    for i, x in zip(s.index, s):
        if is_listy(x):
            l += [(i, xx) for xx in flatten_list(x)]
        else:
            l += [(i, x)]
    il, xl = zip(*l)
    return pd.Series(xl, index=il, name=iname)


def make_counts_df(series: pd.Series) -> pd.Series:
    """This function takes a pandas Series as input and returns a DataFrame
    containing the counts of each unique value in the Series.

    Parameters:
    - series (pandas Series): 
        The input Series containing the values to be counted.
    
    Returns:
    - counts_df (pandas DataFrame): 
        A DataFrame with two columns - `series.name` and 'count'. 
        The `series.name` column contains the unique values from the input Series and bears its name,
        and the 'count' column contains the corresponding counts.
    
    Example:
    >>> series = pd.Series(['apple', 'banana', 'apple', 'orange', 'banana'], name='fruits')
    >>> make_counts_df(series)
         fruits       count
    0    apple            2
    1   banana            2
    2   orange            1
    """
    return pd.DataFrame(
        pd.Series(flatten_list(series),
                  name=series.name).value_counts()).reset_index()


def ordinal_str(n: int) -> str:
    """Derive the ordinal numeral string for a given number n."""
    return f"{n:d}{'tsnrhtdd'[(n//10%10!=1)*(n%10<4)*n%10::4]}"


def force_int(x, errors=0) -> int:
    """Converts the input to an integer.

    Args:
        x: The input value to be converted to an integer.
        errors: The value to be returned in case of an error. Defaults to 0.

    Returns:
        The input value converted to an integer if successful, otherwise the specified error value.
    """
    try:
        return int(x)
    except ValueError:
        return errors


def combine_LR_df(dfL, dfR, colname='L_or_R', colval_L='L', colval_R='R'):
    return pd.concat(
        [dfL.assign(**{colname: colval_L}),
         dfR.assign(**{colname: colval_R})])


# def combine_LR_df_1(dfL, dfR, colname = 'L_or_R', colval_L='L', colval_R='R', colval_LR='LR'):
#     """
#     Combines two dataframes dfL and dfR by joining them on their indexes. The function creates a new column indicating whether a row belongs to the left dataframe, the right dataframe, or both. The resultant dataframe is returned.

#     Args:
#         dfL (pandas.DataFrame): The left dataframe.
#         dfR (pandas.DataFrame): The right dataframe.
#         colname (str, optional): The name of the new column that indicates whether a row belongs to the left dataframe, the right dataframe, or both. Default is 'L_or_R'.
#         colval_L (str, optional): The value in the new column for rows that belong only to the left dataframe. Default is 'L'.
#         colval_R (str, optional): The value in the new column for rows that belong only to the right dataframe. Default is 'R'.
#         colval_LR (str, optional): The value in the new column for rows that belong to both dataframes. Default is 'LR'.

#     Returns:
#         pandas.DataFrame: The combined dataframe.
#     """
#     # logger.debug([dfL.columns, 'dfL cols'])
#     # logger.debug([dfR.columns, 'dfR cols'])
#     assert dfL.index.name == dfR.index.name
#     allL, allR = set(dfL.index), set(dfR.index)
#     print(allR)
#     (
#         onlyL,
#         onlyR,
#         both,
#         either
#      ) = (
#         allL - allR,
#         allR - allL,
#         allR & allL,
#         allR | allL
#      )

#     # logger.debug([len(allL), len(allR), len(both), len(either), 'lens'])

#     def assign(idx, underdog=True):
#         if not onlyL and not onlyR: # nothing distinct
#             o=colval_LR

#         else:
#             # L is underdog, prefer that
#             if len(allL) <= len(allR):
#                 if idx in allL:
#                     o=colval_L
#                 else:
#                     o=colval_R
#             else:
#                 # R is dog
#                 if idx in allR:
#                     o=colval_R
#                 else:
#                     o=colval_L

#         return o

#     odf = pd.concat([dfL, dfR])
#     odf[colname] = [assign(i) for i in odf.index]
#     logger.trace([odf.columns, 'combo cols'])
#     logger.trace([odf.index.name, 'combo index name'])
#     return odf


def serialize(d: object) -> str:
    """Serializes an object into a JSON-encoded string.

    Args:
        d (dict): The object to be serialized.

    Returns:
        str: A JSON-encoded string that represents the serialized object.
    """
    return orjson.dumps(d, option=orjson.OPT_SORT_KEYS).decode()


def unserialize(dstr: str) -> object:
    """Deserializes a JSON-encoded string into a python object.

    Args:
        dstr (str): The JSON-encoded string to be deserialized.

    Returns:
        dict: A object representing the deserialized JSON.
    """
    return orjson.loads(dstr)


def selectrename_df(df: pd.DataFrame, col2col: dict = {}) -> pd.DataFrame:
    """Selects and renames columns in a DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame to select and rename columns from.
        col2col (dict): A dictionary mapping old column names to new column names. The keys of the dictionary are the old column names, and the values are the new column names.
    
    Returns:
        pandas.DataFrame: A new DataFrame with selected and renamed columns.
    
    Example:
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
        >>> col2col = {'A': 'X', 'B': 'Y'}
        >>> selectrename_df(df, col2col)
           X  Y
        0  1  4
        1  2  5
        2  3  6
    
    Note:
        - If a column in col2col is not present in the DataFrame, it will be ignored.
        - If a column in col2col is present in the DataFrame but not specified in col2col, it will be dropped from the resulting DataFrame.
    """
    c2c = {k: v for k, v in col2col.items() if k in set(df.columns)}
    return df[c2c.keys()].rename(columns=c2c)


def is_numeric_ish(x: str):
    try:
        float(x)
        return True
    except (TypeError, ValueError):
        return False


def is_quant_series(series, ish=False):
    return all(is_numeric(x) or (ish and is_numeric_ish(x)) for x in series)


def qualquant_series(series, quant=False, drop_na=False, drop_empty=False):
    """This function takes a series as input and converts it into a pandas
    Series object if it is not already. If the 'quant' parameter is set to
    True, it converts the series into numeric values using the 'pd.to_numeric'
    function with 'coerce' error handling. If 'quant' is set to False, it fills
    any missing values with an empty string and converts the series into a
    string representation using the 'apply' and 'replace' functions.

    Parameters:
    - series: The input series to be converted. It can be either a pandas Series object or a list-like object.
    - quant: A boolean parameter indicating whether to convert the series into numeric values (True) or string representation (False). Default is False.

    Returns:
    - A pandas Series object with the converted values.
    """
    series = pd.Series(series) if type(series) != pd.Series else series
    if quant is True:
        series = pd.to_numeric(series, errors='coerce')
        if drop_na: series = series.dropna()
    elif quant is False:
        series = series.fillna('').apply(str)
        if drop_empty: series = series[series != '']
    return series


def uid(length=10):
    """Generates a unique identifier (UID) using the shortuuid library.

    Args:
        length (int, optional): The length of the UID to be generated. Defaults to 10.
    
    Returns:
        str: A randomly generated unique identifier of the specified length.
    
    Example:
        >>> uid()
        '2bXw7n3e9R'
        >>> uid(8)
        '1A7b9C5d'
    """
    import shortuuid
    return str(shortuuid.ShortUUID().random(length=length))


class Logwatch:
    """A class for monitoring and logging the duration of tasks.

    Attributes:
        started (float): The timestamp when the task started.
        ended (float): The timestamp when the task ended.
        level (str): The logging level for the task. Default is 'DEBUG'.
        log (Logger): The logger object for logging the task status.
        task_name (str): The name of the task being monitored.
    """

    def __init__(self, name=None, level='DEBUG'):
        self.started = None
        self.ended = None
        self.level = level
        self.log = getattr(logger, self.level.lower())
        self.task_name = name

    @property
    def tdesc(self):
        """Returns the formatted timespan of the duration.
        
        Returns:
            str: The formatted timespan of the duration.
        
        Examples:
            >>> t = tdesc(self)
            >>> print(t)
            '2 hours 30 minutes'
        """
        return format_timespan(self.duration)

    @property
    def duration(self):
        """Calculates the duration of an event.
        
        Returns:
            float: The duration of the event in seconds.
        """
        return self.ended - self.started

    @property
    def desc(self):
        """Returns a description of the task.
        
        If the task has both a start time and an end time, it returns a string
        indicating the task name and the time it took to complete the task.
        
        If the task is currently running, it returns a string indicating that
        the task is still running.
        
        Returns:
            str: A description of the task.
        """
        if self.started is not None and self.ended is not None:
            return f'{self.task_name} ... {self.tdesc}'
        else:
            return f'Task running ...' if not self.task_name else f'{self.task_name} ...'

    def __enter__(self):
        """Context manager method that is called when entering a 'with' statement.
        
        This method logs the description of the context manager and starts the timer.
        
        Examples:
            with Logwatch():
                # code to be executed within the context manager
        """
        self.log(self.desc)
        self.started = time.time()
        return self

    def __exit__(self, *x):
        """
        Logs the resulting time.
        """
        self.ended = time.time()
        self.log(self.desc)


def is_range_of_ints(numbers: 'Iterable') -> bool:
    """Check if the given numbers form a range of integers.
    
    Args:
        numbers (Iterable): A collection of numbers.
    
    Returns:
        bool: True if the numbers form a range of integers, False otherwise.
    
    Examples:
        >>> is_range_of_ints([1, 2, 3, 4, 5])
        True
        >>> is_range_of_ints([1, 2, 4, 5])
        False
        >>> is_range_of_ints([1, 2, 3, 3, 4, 5])
        False
    """

    l = numbers
    if not is_listy(l): return False
    if len(l) < 2: return False
    try:
        if any(x != int(x) for x in l): return False
    except ValueError:
        return False
    l = list(sorted(int(x) for x in l))
    return l == list(range(l[0], l[-1] + 1))


def delist_df(df: pd.DataFrame, sep: str = ' ', human=True) -> pd.DataFrame:
    """
    Takes a pandas DataFrame (df), iterates through each column, 
    and applies the function fix to each value in each column. The function 
    fix turns list-like objects into strings, rounds numeric objects to 
    two decimal places, and leaves all other types of objects unchanged. 

    If an item in a column is a list-like object, it joins the items in the list
    into a string, separated by the provided separator (default is a space). If an 
    item is a numeric value, it rounds the number to two decimal places.
    The function returns a new DataFrame. The original DataFrame remains unchanged.

    Args:
        df (pd.DataFrame): The DataFrame to process.
        sep (str, optional): The separator to use when joining list-like objects into strings.
                             Default is a space.

    Returns:
        pd.DataFrame: The processed DataFrame.
    """

    def fix(y):
        if is_listy(y): 
            if human:
                return delistify(y)
            else:
                return sep.join(str(x) for x in y)
        elif is_numeric(y): 
            return round(y, 2)
        else:
            return y

    # df = df.copy()
    # for col in df:
    #     df[col] = df[col].apply(fix)
    return df.applymap(fix)


def oxfordcomma(l, repr=repr, op='and'):
    """Join a list of elements with an Oxford comma.
    
    Args:
        l (list): The list of elements to join.
        repr (function, optional): The function used to represent each element as a string. Defaults to repr.
        op (str, optional): The conjunction used before the last element. Defaults to 'and'.
    
    Returns:
        str: The joined string with an Oxford comma.
    """

    if len(l) < 3:
        return f' {op} '.join(repr(x) for x in l)
    else:
        return f"{', '.join(repr(x) for x in l[:-1])}, {op} {repr(l[-1])}"


def ifnanintstr(x, y=''):
    return ensure_int(x) if not np.isnan(x) else y


def postproc_df(
    df,
    cols=[],  # or dict to rename
    cols_sep=[],
    cols_q=[],
    cols_pref=[],
    sep=';',
    fillna=None,
):

    # sep?
    cols_qset = set(cols_q)

    def split_sep_col(x, quant, sep):
        if is_listy(x):
            l = x
        else:
            l = [y.strip() for y in str(x).split(sep)]

        if quant:
            l = [pd.to_numeric(y, errors='coerce') for y in l]

        return l

    for c in cols_sep:
        df[c] = df[c].fillna('').apply(
            lambda x: split_sep_col(x, c in cols_qset, sep))

    # rename?
    if cols:
        df = df[cols] if is_listy(cols) else selectrename_df(df, cols)

    # quantize?
    for c in cols_q:
        if c not in set(cols_sep) and c in set(df.columns):
            df[c] = pd.to_numeric(df[c], errors='coerce')

    # prefcols
    if cols_pref:
        cl1 = [c for c in cols_pref if c in set(df.columns)]
        cl2 = [c for c in df if c not in set(cols_pref)]
        df = df[cl1 + cl2]

    if fillna is not None:
        df = df.fillna(fillna)

    return df


def get_date_cmp(*l):
    l = [str(x) for x in l]
    minlen = min([len(x) for x in l])
    return [x[:minlen] for x in l]


def date_fuzzily_precedes(x, y):
    x2, y2 = get_date_cmp(x, y)
    return x2 < y2


def date_fuzzily_follows(x, y):
    x2, y2 = get_date_cmp(x, y)
    return x2 > y2


def is_fuzzy_date_seq(x, y, z):
    if any(not _ for _ in [x, y, z]): return False

    x, y, z = get_date_cmp(x, y, z)
    return x <= y <= z


def ensure_dir(fn):
    dirname = os.path.dirname(fn)
    if not os.path.exists(fn):
        try:
            os.makedirs(dirname)
            logger.debug(f'{dirname} created')
        except Exception as e:
            logger.warning(e)


def rejoin_sep(listy_obj, sep=','):
    if not is_listy(listy_obj): return listy_obj
    o = sep.join(str(x) for x in listy_obj if x)
    while o.startswith('~,'):
        o = '~' + o[2:]
    return o


def compressed_bytes(obj):
    """Compresses the given object into a base64 encoded string.
    
    Args:
        obj: The object to be compressed.
    
    Returns:
        str: The base64 encoded string representing the compressed object.
    """

    ojson_b = orjson.dumps(obj, option=orjson.OPT_SERIALIZE_NUMPY)
    ojson_bz = zlib.compress(ojson_b)
    ojson_bz64 = b64encode(ojson_bz)
    return ojson_bz64


def uncompressed_bytes(ojson_bz64):
    if type(ojson_bz64) == str: ojson_bz64 = ojson_bz64.encode()
    ojson_bz = b64decode(ojson_bz64)
    ojson_b = zlib.decompress(ojson_bz)
    ojson = orjson.loads(ojson_b)
    return ojson


def compressed_str(obj):
    """Return a compressed string representation of the given object.
    
    Args:
        obj: The object to be compressed.
    
    Returns:
        str: The compressed string representation of the object.
    
    Note:
        This function internally uses the `compressed_bytes` function to compress the object and then decodes the compressed bytes using 'utf-8' encoding.
    """

    return compressed_bytes(obj).decode('utf-8')


def uncompressed_str(x):
    return uncompressed_bytes(x)


def compress_to(obj, fn):
    """Compresses the given object and writes the compressed bytes to a file.
    
    Args:
        obj: The object to be compressed.
        fn: The filename of the file to write the compressed bytes to.
    
    Returns:
        None
    
    Raises:
        IOError: If there is an error while writing to the file.
    """

    with open(fn, 'wb') as of:
        of.write(compressed_bytes(obj))


def uncompress_from(fn):
    with open(fn, 'rb') as of:
        return uncompressed_bytes(of.read())


def get_query_params(qstr: str) -> dict:
    """Returns a dictionary of query parameters from the given query string.
    
    Args:
        qstr (str): The query string containing the parameters.
    
    Returns:
        dict: A dictionary containing the query parameters.
    
    Example:
        >>> get_query_params('?name=John&age=25')
        {'name': 'John', 'age': '25'}
    """
    from urllib.parse import parse_qs
    if not qstr: return {}
    if qstr.startswith('?'): qstr = qstr[1:]
    if not qstr: return {}
    params = parse_qs(qstr)
    return dict(params) if params else {}




def delistify(input_list, sep=', '):
    if not is_listy(input_list):
        return str(input_list)
    elif len(input_list)==0:
        return ""
    elif len(input_list)==1:
        return input_list[0]
    else:
        try:
            sorted_list = sorted(int(item) for item in input_list)
            a,b = sorted_list[0], sorted_list[-1]
            return f'{a} to {b}'
        except ValueError:
            return sep.join(sorted(str(x) for x in input_list))
