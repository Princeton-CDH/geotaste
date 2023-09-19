from .imports import *
from scipy.stats.contingency import odds_ratio
from scipy.stats import fisher_exact
from tqdm import tqdm


def analyze_contingency_tables(
        vals1, 
        vals2, 
        funcs = [odds_ratio, fisher_exact], 
        sort_by='odds_ratio', 
        p_col='fisher_exact_p',
        sort_asc=True, 
        min_p=MIN_P,
        signif=False):
    """
    Analyzes contingency tables created from two input value series.

    Args:
        vals1 (pd.Series): The first value series.
        vals2 (pd.Series): The second value series.
        funcs (list, optional): List of statistical functions to apply to each contingency table. Defaults to [odds_ratio, fisher_exact].
        sort_by (str, optional): The column to sort the resulting DataFrame by. Defaults to 'odds_ratio'.
        p_col (str, optional): The column containing p-values. Defaults to 'fisher_exact_p'.
        sort_asc (bool, optional): Whether to sort the DataFrame in ascending order. Defaults to True.
        min_p (float, optional): The minimum p-value threshold. Defaults to MIN_P.
        signif (bool, optional): Whether to filter the DataFrame by p-value threshold. Defaults to False.

    Returns:
        pd.DataFrame: The resulting DataFrame containing the analyzed contingency tables.
    """

    vals1=pd.Series(vals1)
    vals2=pd.Series(vals2)
    index_name='__'.join(sorted(list(set([vals1.name, vals2.name]))))
    ld=[]
    vals_ctbls = list(iter_contingency_tables(vals1, vals2))
    for val,ctbl in vals_ctbls:
        val_d = {
            'value':val, 
            **table_info(ctbl)
        }
        for func in funcs:
            res = func(ctbl)
            method=func.__name__
            stat=res.statistic if hasattr(res,'statistic') else None
            pval=res.pvalue if hasattr(res,'pvalue') else None
            if stat is not None: val_d[f'{method}'] = stat
            if pval is not None: val_d[f'{method}_p'] = pval
        
        ld.append(val_d)
    df = pd.DataFrame(ld)
    if len(df):
        df=df.set_index('value')
        if signif and p_col: df = df[df[p_col]<=min_p]
    df = df.rename_axis(index_name)
    df = df.sort_values(sort_by, ascending=sort_asc) if sort_by and len(df) else df
    return df


def iter_contingency_tables(vals1:'Iterable', vals2:'Iterable', uniqvals:'Iterable'=[], min_count:int=None):
    """
    Iterates over contingency tables for two sets of values.

    Args:
        vals1 (Iterable): The first set of values.
        vals2 (Iterable): The second set of values.
        uniqvals (Iterable, optional): A list of unique values to consider. Defaults to an empty list.
        min_count (int | None, optional): The minimum count required for a contingency table to be yielded. Defaults to None.

    Yields:
        tuple: A tuple containing the unique value and its corresponding contingency table.
    """
    
    assert is_listy(vals1),is_listy(vals2)
    s1,s2=pd.Series(vals1),pd.Series(vals2)
    counts1,counts2=s1.value_counts(), s2.value_counts()
    uniqvals = set(s1)|set(s2) if not uniqvals else set(uniqvals)

    def get_contingency_table(v):
        tl=int(counts1.get(v,0))
        tr=int(counts2.get(v,0))
        bl=int((counts1.sum() if len(counts1) else 0) - tl)
        br=int((counts2.sum() if len(counts2) else 0) - tr)
        return ((tl,tr),(bl,br))
    
    def total_count(tbl): return sum(tbl[0]) + sum(tbl[1])

    for uniqval in uniqvals:
        tbl = get_contingency_table(uniqval)
        if min_count is None or total_count(tbl) >= min_count:
            yield (uniqval, tbl)




def table_info(ctbl):
    """Returns a dictionary containing information about a given table.
    
    Args:
        ctbl (list): A 2D list representing the table:
            [
                [count_L, count_R],
                [total_L, total_R]
            ]
    
    Returns:
        dict: A dictionary containing the following information:
            - count_sum (int): The sum of count1 and count2.
            - count_min (int): The minimum value between count1 and count2.
            - count_L (int): The value of count1.
            - count_R (int): The value of count2.
            - perc_L (float): The percentage of count1 relative to support1.
            - perc_R (float): The percentage of count2 relative to support2.
            - perc_L->R (float): The difference between perc_R and perc_L.
    
    Examples:
        >>> table_info([[10, 20], [30, 40]])
        {'count_sum': 30, 'count_min': 10, 'count_L': 10, 'count_R': 20, 'perc_L': 25.0, 'perc_R': 33.33333333333333, 'perc_L->R': 8.333333333333329}
        >>> table_info([[0, 0], [0, 0]])
        {'count_sum': 0, 'count_min': 0, 'count_L': 0, 'count_R': 0, 'perc_L': nan, 'perc_R': nan, 'perc_L->R': nan}
    """
    
    count1=ctbl[0][0]
    count2=ctbl[0][1]
    support1=ctbl[0][0] + ctbl[1][0]
    support2=ctbl[0][1] + ctbl[1][1]
    perc1=count1/support1*100 if support1 else np.nan
    perc2=count2/support2*100 if support2 else np.nan
    perc_diff=perc2-perc1
    return {
        'count_sum':count1+count2,
        'count_min':min([count1,count2]),
        'count_L':count1,
        'count_R':count2,
        'perc_L':perc1,
        'perc_R':perc2,
        'perc_L->R':perc_diff,
    }




def filter_signif(df, p_col=None, min_p=MIN_P):
    """Filters a DataFrame based on the significance level of a specified column.
    
    Args:
        df (pandas.DataFrame): The DataFrame to be filtered.
        p_col (str, optional): The name of the column containing p-values. If not provided, the function will attempt to find a column named 'pvalue' or ending with '_p'. Defaults to None.
        min_p (float, optional): The minimum p-value threshold for filtering. Rows with p-values greater than this threshold will be removed. Defaults to MIN_P.
    
    Returns:
        pandas.DataFrame: The filtered DataFrame.
    
    Examples:
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [0.05, 0.1, 0.2]})
        >>> filter_signif(df, min_p=0.1)
           A     B
        0  1  0.05
        1  2  0.10
    """
    
    if min_p is None: return df
    if p_col is None: p_col=first([c for c in df if c=='pvalue' or c.endswith('_p')])
    if not p_col: return df
    return df[df[p_col] <= min_p]


def geodist(latlon1, latlon2, unit='km'):
    """Calculates the geodesic distance between two points given their latitude and longitude coordinates.
    
    Args:
        latlon1 (tuple): A tuple containing the latitude and longitude coordinates of the first point.
        latlon2 (tuple): A tuple containing the latitude and longitude coordinates of the second point.
        unit (str, optional): The unit of measurement for the distance. Defaults to 'km'.
    
    Returns:
        float: The geodesic distance between the two points in the specified unit.
    
    Raises:
        ValueError: If the latitude or longitude coordinates are invalid.
    """
    
    from geopy.distance import geodesic as distfunc
    import numpy as np
    try:
        dist = distfunc(
            (latlon1[1],latlon1[0]), 
            (latlon2[1],latlon2[0])
        )
        return getattr(dist,unit)
    except ValueError as e:
        return np.nan
    
def get_dist_from_SCO(lat,lon):
    """Calculate the distance from a given latitude and longitude to the coordinates of SCO.
    
    Args:
        lat (float): The latitude of the location.
        lon (float): The longitude of the location.
    
    Returns:
        float: The distance in kilometers from the given location to SCO.
    """    
    return geodist((lat,lon), LATLON_SCO)







# @cache_obj.memoize()
def get_distinctive_qual_vals(
        dfL,
        dfR,
        maxcats=100,
        cols=[
            'member_title', 
            'member_gender', 
            'member_nationalities',
            # 'event_type',
            'creator_gender',
            # 'creator_role',
            'creator_nationalities',
            'book_format',
            'book_genre',
            'arrond_id'
        ],
        only_signif=False,
        round=4,
        min_count=1,
        min_sum=10,
        drop_duplicates=[],
        drop_empty=True
        ):
    """Calculates distinctive qualitative values between two dataframes.
    
    Args:
        dfL (DataFrame): Left dataframe.
        dfR (DataFrame): Right dataframe.
        maxcats (int, optional): Maximum number of categories allowed for a column. Defaults to 100.
        cols (list, optional): List of columns to analyze. Defaults to ['member_title', 'member_gender', 'member_nationalities', 'creator_gender', 'creator_nationalities', 'book_format', 'book_genre', 'arrond_id'].
        only_signif (bool, optional): Flag to return only significant values. Defaults to False.
        round (int, optional): Number of decimal places to round the results. Defaults to 4.
        min_count (int, optional): Minimum count required for a value to be considered. Defaults to 1.
        min_sum (int, optional): Minimum sum required for a value to be considered. Defaults to 10.
        drop_duplicates (list or dict, optional): Columns to drop duplicates by. Defaults to [].
        drop_empty (bool, optional): Flag to drop empty values. Defaults to True.
    
    Returns:
        DataFrame: Distinctive qualitative values between the two dataframes.
    
    Examples:
        >>> dfL = pd.DataFrame({'col1': ['A', 'B', 'C'], 'col2': ['X', 'Y', 'Z']})
        >>> dfR = pd.DataFrame({'col1': ['A', 'B', 'D'], 'col2': ['X', 'Y', 'W']})
        >>> get_distinctive_qual_vals(dfL, dfR)
           col col_val comparison_scale  odds_ratio  perc_L  perc_R  count_L  count_R
        0  col1       C                    0.000000     0.0     0.0      0.0      0.0
        1  col2       Z                    0.000000     0.0     0.0      0.0      0.0
    """
    
        
    o=[]

    if drop_duplicates:
        if is_listy(drop_duplicates) or type(drop_duplicates)==str:
            dfL=dfL.drop_duplicates(drop_duplicates)
            dfR=dfR.drop_duplicates(drop_duplicates)


    if cols is None: cols=list(set(dfL.columns) & set(dfR.columns))
    
    for col in cols:
        try:
            colpref=col.split('_')[0]
            if drop_duplicates and type(drop_duplicates)==dict:
                if col in drop_duplicates: 
                    dedupby=drop_duplicates[col] 
                elif colpref in drop_duplicates:
                    dedupby=drop_duplicates[colpref]
                
                dfLnow = dfL.drop_duplicates(dedupby)
                dfRnow = dfR.drop_duplicates(dedupby)
            else:
                dedupby = []
                dfLnow = dfL
                dfRnow = dfR
                    
            s1=qualquant_series(flatten_series(dfLnow[col]), quant=False, drop_empty=drop_empty)
            s2=qualquant_series(flatten_series(dfRnow[col]), quant=False, drop_empty=drop_empty)

            if maxcats and (s1.nunique()>maxcats or s2.nunique()>maxcats):
                continue

            coldf = analyze_contingency_tables(s1, s2)
            coldf = coldf.query(
                f'count_min>={min_count} & count_sum>={min_sum}'
            ).assign(
                col=col,
                comparison_scale=' '.join(dedupby)
            )
            o.append(coldf)
        except Exception as e:
            logger.error(e)

    if not len(o): return pd.DataFrame()

    alldf=pd.concat(o).rename_axis('col_val').reset_index()
    alldf=alldf.replace([np.inf, -np.inf], np.nan).dropna()
    alldf=alldf[alldf.fisher_exact!=0] # both must have counts?
    alldf['odds_ratio_log']=alldf['odds_ratio'].apply(np.log10)
    alldf['odds_ratio_pos']=alldf['odds_ratio'].apply(lambda x: 1/x if x<1 else x)
    alldf=alldf[~alldf.col_val.str.contains('\n')]
    prefcols=['col','col_val','comparison_scale','odds_ratio','perc_L','perc_R','count_L','count_R']
    cols = prefcols + [c for c in alldf if c not in set(prefcols)]
    alldf=alldf[cols].sort_values('fisher_exact',ascending=False)
    sigdf=alldf.query('fisher_exact_p<=0.05')

    return (sigdf if only_signif else alldf).round(round)




def describe_comparison(comparison_df, lim=10, min_fac=1.1):
    """Describe the comparison between two groups based on a comparison dataframe.
    
    Args:
        comparison_df (DataFrame): The comparison dataframe containing the data for comparison.
        lim (int, optional): The maximum number of rows to include in the description. Defaults to 10.
        min_fac (float, optional): The minimum odds ratio threshold. Rows with odds ratio below this threshold will be excluded. Defaults to 1.1.
    
    Returns:
        tuple: A tuple containing two lists of descriptions. The first list describes the comparison for group L, and the second list describes the comparison for group R.
    
    Examples:
        >>> df = pd.DataFrame({'col': ['A', 'B', 'C'], 'col_val': ['X', 'Y', 'Z'], 'perc_L': [50, 60, 70], 'perc_R': [40, 30, 20], 'count_L': [100, 200, 300], 'count_R': [50, 100, 150], 'fisher_exact_p': [0.05, 0.1, 0.01], 'odds_ratio_pos': [1.5, 1.2, 1.8]})
        >>> desc_L, desc_R = describe_comparison(df, lim=2, min_fac=1.2)
        >>> print(desc_L)
        * *1.80x* likelier for Col to be **X** **
        * Group 1: 70.0% (300 of 428.6)
        * Group 2: 20.0% (150 of 750.0)
        * *1.50x* likelier for Col to be **Y** **
        * Group 1: 60.0% (200 of 333.3)
        * Group 2: 30.0% (100 of 333.3)
    
        >>> print(desc_R)
        * *1.80x* likelier for Col to be **X** **
        * Group 1: 40.0% (100 of 250.0)
        * Group 2: 70.0% (300 of 428.6)
        * *1.20x* likelier for Col to be **Y** **
        * Group 1: 30.0% (50 of 166.7)
        * Group 2: 60.0% (200 of 333.3)
    """
    
    idf=comparison_df.sort_values('odds_ratio_pos',ascending=False)
    L,R=idf.query('perc_L>perc_R'),idf.query('perc_R>perc_L')

    def get_list_desc(xdf, LR='L'):
        LR2='R' if LR=='L' else 'L'
        o=[]
        for i,row in xdf.iterrows():
             if min_fac and row.odds_ratio_pos<min_fac: continue
             pL=row[f'perc_{LR}']
             pR=row[f'perc_{LR2}']
             cL=row[f'count_{LR}']
             cR=row[f'count_{LR2}']
             tL=cL/(pL/100)
             tR=cR/(pR/100)
             p=row.fisher_exact_p
             pstr='\*\*\*' if p<0.01 else ('\*\*' if p<0.05 else ('\*' if p<0.1 else ''))
             colval=row.col_val.replace("[","\[").replace("]","\]")
             orow=f'''* *{row.odds_ratio_pos:.2f}x* likelier for {row.col.replace("_id","").replace("_"," ").title()} to be **{colval}** {pstr}
    * Group 1: {pL:.1f}% ({cL:.0f} of {tL:,.0f})
    * Group 2: {pR:.1f}% ({cR:.0f} of {tR:,.0f})
'''
             o.append(orow)
             if lim and len(o)>=lim: break
        return o
    
    return get_list_desc(L), get_list_desc(R)

    
    
    


