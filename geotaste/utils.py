from .imports import *

def hasone(x:list, y:list) -> bool:
    """Checks if there is at least one common element between two lists.

    Args:
        x (list): The first list.
        y (list): The second list.

    Returns:
        bool: True if there is at least one common element between the two lists, False otherwise.
    """
    res = bool(set(x)&set(y))
    return res

def isin(x:object, y:list) -> bool:
    """Checks if an object is present in a given list.

    Args:
        x (object): The object to be checked.
        y (list): The list in which the object is checked.

    Returns:
        bool: True if the object is present in the list, False otherwise.
    """
    res = bool(x in set(y))
    return res

def isin_or_hasone(x:object, y:list) -> bool:
    """Check if an object is in a list or has at least one element in a list.

    Args:
        x (object): The object to check.
        y (list): The list to check against.

    Returns:
        bool: True if the object is in the list or has at least one element in the list, False otherwise.
    """
    
    if not is_listy(y): 
        y={y}
    else:
        y=set(y)
    if type(x) in {list,set,tuple}:
        return hasone(x,y)
    else:
        return isin(x,y)
    
def to_set(x:object) -> set:
    """Converts a value to a set.

    Args:
        x: The value to be converted.

    Returns:
        A set containing the value `x` if `x` is not a list-like object, otherwise a set containing all the elements of `x`.
    """
    return {x} if not is_listy(x) else set(flatten_list(x))
    
def overlaps(series:pd.Series, vals:list) -> pd.Series:
    """Checks if any element in the given series overlaps with the values in
    the given list.

    Args:
        series (pandas.Series): The series to check for overlaps.
        vals (list): The list of values to check for overlaps with the series.

    Returns:
        pandas.Series: A boolean series indicating if each element in the series overlaps with any value in the list.
    """
    vals_set = to_set(vals)
    series_set = series.apply(to_set)
    return series_set.apply(lambda xset: bool(xset & vals_set))

def is_numeric(x:object) -> bool:
    """Checks if the given object is a numeric value.

    Args:
        x (object): The object to be checked.

    Returns:
        bool: True if the object is a numeric value, False otherwise.
    """
    return isinstance(x, numbers.Number)

def is_numberish(x:object) -> bool:
    return is_numeric(x) or (type(x)==str and x.isdigit())

def is_listy(x:object) -> bool:
    """Checks if the input object is a list-like object.

    Args:
        x (object): The object to be checked.

    Returns:
        bool: True if the object is a tuple, list, or pandas Series; False otherwise.
    """
    return type(x) in {tuple,list,pd.Series}

def ensure_int(x:Number, return_orig=True, default=None) -> int:
    try:
        return int(x)
    except ValueError:
        return (x if return_orig else default)

def ensure_dict(x:object) -> dict:
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

def find_plural_cols(df:pd.DataFrame) -> list:
    """Finds the columns in a pandas DataFrame that contain lists.

    Args:
        df (pandas.DataFrame): The DataFrame to search for columns with lists.

    Returns:
        list: A list of column names that contain lists.
    """
    return list(df.columns[(df.applymap(type) == list).any()])

def first(l:Iterable, default:object=None) -> object:
    """Returns the first element of an iterable object.

    Args:
        l (Iterable): The iterable object, e.g. a list.
        default (object, optional): The default value to return if the iterable is empty. Defaults to None.

    Returns:
        object: The first element of the iterable, or the default value if the iterable is empty.
    """
    for x in l: return x
    return default

def flatten_list(s:Iterable) -> list:
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
    l=[]
    for x in s:
        if is_listy(x):
            l+=flatten_list(x)
        else:
            l+=[x]
    return l

def flatten_series(s:pd.Series) -> pd.Series:
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
    s=pd.Series(s)
    l=[]
    for i,x in zip(s.index, s):
        if is_listy(x):
            l+=[(i,xx) for xx in flatten_list(x)]
        else:
            l+=[(i,x)]
    il,xl=zip(*l)
    return pd.Series(xl,index=il)

def make_counts_df(series:pd.Series) -> pd.Series:
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
        pd.Series(
            flatten_list(series), 
            name=series.name
        ).value_counts()
    ).reset_index()

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
    

class CachedData:
    """A class for caching data using SqliteDict.

    Attributes:
        path_cache (str): The path to the cache file. If not an absolute path, join the path to `PATH_DATA` constant defined elsewhere.
    """
    def __init__(self, *x, path_cache=None, **y):
        self.path_cache = (
            os.path.join(PATH_DATA, path_cache) 
            if path_cache and not os.path.isabs(path_cache) 
            else path_cache
        )

    def cache(self, tablename='unnamed', flag='c', autocommit=True, **kwargs) -> 'SqliteDict':
        """Caches data using SqliteDict.

        Args:
            tablename (str): The name of the table in the cache.
            flag (str): The flag indicating the mode of the cache.
            autocommit (bool): Whether to automatically commit changes to the cache.
            **kwargs: Additional keyword arguments.

        Returns:
            SqliteDict: The SqliteDict object representing the cache.
        """
        return SqliteDict(
            filename=self.path_cache, 
            tablename=tablename, 
            flag=flag,
            autocommit=autocommit,
            **kwargs
        )
    
def concat_LR_df(dfL, dfR, colname = 'L_or_R', colval_L='L', colval_R='R', colval_LR='LR'):
    return pd.concat([
        dfL.assign(**{colname:colval_L}),
        dfR.assign(**{colname:colval_R})
    ]).sample(frac=1)


def combine_LR_df(dfL, dfR, colname = 'L_or_R', colval_L='L', colval_R='R', colval_LR='LR'):
    """
    Combines two dataframes dfL and dfR by joining them on their indexes. 
    The function creates a new column indicating whether a row belongs to the left dataframe, 
    the right dataframe, or both. The resultant dataframe is returned.

    Args:
        dfL (pandas.DataFrame): The left dataframe.
        dfR (pandas.DataFrame): The right dataframe.
        colname (str, optional): The name of the new column that indicates whether a row 
                                 belongs to the left dataframe, the right dataframe, 
                                 or both. Default is 'L_or_R'.
        colval_L (str, optional): The value in the new column for rows that belong 
                                  only to the left dataframe. Default is 'L'.
        colval_R (str, optional): The value in the new column for rows that belong 
                                  only to the right dataframe. Default is 'R'.
        colval_LR (str, optional): The value in the new column for rows that belong 
                                   to both dataframes. Default is 'LR'.

    Returns:
        pandas.DataFrame: The combined dataframe.
    """
    # logger.debug([dfL.columns, 'dfL cols'])
    # logger.debug([dfR.columns, 'dfR cols'])
    print(dfL.index.name, dfR.index.name)
    assert dfL.index.name == dfR.index.name
    allL, allR = set(dfL.index), set(dfR.index)
    print(allR)
    (
        onlyL, 
        onlyR, 
        both,
        either
     ) = (
        allL - allR, 
        allR - allL, 
        allR & allL,
        allR | allL
     )
    
    
    logger.debug([len(allL), len(allR), len(both), len(either), 'lens'])

    def assign(idx, underdog=True):
        if not onlyL and not onlyR: # nothing distinct
            o=colval_LR

        else:
            # L is underdog, prefer that
            if len(allL) <= len(allR):
                if idx in allL:
                    o=colval_L
                else:
                    o=colval_R
            else:
                # R is dog
                if idx in allR:
                    o=colval_R
                else:
                    o=colval_L
        
            if 'hemingway' in str(idx):
                logger.debug([idx,idx in allL, idx in allR, idx in both, idx in either, '->',o])
        
        return o

    logger.debug(dfL.member_gender.value_counts())
    logger.debug(dfR.member_gender.value_counts())
    odf = pd.concat([dfL, dfR])
    odf[colname] = [assign(i) for i in odf.index]
    # odf = odf#.reset_index().drop_duplicates([odf.index.name,colname]).set_index(odf.index.name)
    logger.debug([odf.columns, 'combo cols'])
    logger.debug([odf.index.name, 'combo index name'])
    return odf




def serialize(d:object) -> str:
    """Serializes an object into a JSON-encoded string.

    Args:
        d (dict): The object to be serialized.

    Returns:
        str: A JSON-encoded string that represents the serialized object.
    """
    return orjson.dumps(d, option=orjson.OPT_SORT_KEYS).decode()

def unserialize(dstr:str) -> object:
    """Deserializes a JSON-encoded string into a python object.

    Args:
        dstr (str): The JSON-encoded string to be deserialized.

    Returns:
        dict: A object representing the deserialized JSON.
    """
    return orjson.loads(dstr)



def nowstr():
    """Returns the current date and time as a formatted string.

    Returns:
        str: A string representing the current date and time in the format "YYYY-MM-DD HH:MM:SS.SSS".
    
    Example:
        >>> nowstr()
        '2022-01-01 12:30:45.123'
    """
    from datetime import datetime
    current_datetime = datetime.now()
    friendly_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return friendly_string

def selectrename_df(df:pd.DataFrame, col2col:dict={}) -> pd.DataFrame:
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
    c2c = {k:v for k,v in col2col.items() if k in set(df.columns)}
    return df[c2c.keys()].rename(columns=c2c)

def qualquant_series(series, quant=False):
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
    series=pd.Series(series) if type(series)!=pd.Series else series
    if quant is True: 
        series=pd.to_numeric(series, errors='coerce')
    elif quant is False:
        series=series.fillna('').apply(str)
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
        self.level=level
        self.log = getattr(logger,self.level.lower())
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

    def __exit__(self,*x):
        """
        Logs the resulting time.
        """ 
        self.ended = time.time()
        self.log(self.desc)

class Logmaker:
    """A class that provides logging functionality.

    Attributes:
        None

    Methods:
        log(*x, level='debug', **y): Logs the given message with the specified level.
    """
    def log(self, *x, level='debug', **y):
        """Logs the given message with the specified level.

        Args:
            *x: Variable length argument list of values to be logged.
            level (str): The log level to be used. Default is 'debug'.
            **y: Variable length keyword argument list of additional values to be logged.

        Returns:
            None

        Raises:
            None
        """
        o=' '.join(str(xx) for xx in x)
        name=self.__class__.__name__
        if hasattr(self,'name'): name+=f' ({self.name})'
        o = f'[{nowstr()}] {name}: {o}'
        f=getattr(logger,level)
        f(o)

def is_range_of_ints(numbers:'Iterable') -> bool:
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
    if len(l)<2: return False
    try:
        if any(x!=int(x) for x in l): return False
    except ValueError:
        return False
    l = list(sorted(int(x) for x in l))
    return l == list(range(l[0], l[-1]+1))



def delist_df(df:pd.DataFrame, sep:str=' ') -> pd.DataFrame:
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
        if is_listy(y): return sep.join(str(x) for x in y)
        if is_numeric(y): y=round(y,2)
        return y
    df=df.copy()
    for col in df:
        df[col]=df[col].apply(fix)
    return df



def oxfordcomma(l, repr=repr, op='and'):
    if len(l)<3:
        return f' {op} '.join(repr(x) for x in l)
    else:
        return f"{', '.join(repr(x) for x in l[:-1])}, {op} {repr(l[-1])}"
    


def wraptxt(s, n, newline_char='\n'):
    """
    Args:
    s (str): String to be wrapped.
    n (int): Number of characters after which the string should be wrapped.
    newline_char (str): The character to be inserted at the end of each wrapped line. Default is '\n'.

    Returns:
    str: The wrapped string.
    """
    words = s.split()
    lines = []
    current_line = ''
    for word in words:
        if len(current_line) + len(word) > n:
            lines.append(current_line.strip())
            current_line = word
        else:
            current_line += ' ' + word
    lines.append(current_line.strip())
    return newline_char.join(lines)

def wraphtml(x,xn=50): return wraptxt(x, ensure_int(xn), '<br>') if x else x

def ifnanintstr(x,y='?'):
    return ensure_int(x) if not np.isnan(x) else y