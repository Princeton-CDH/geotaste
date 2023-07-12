from .imports import *
from scipy.stats.contingency import odds_ratio
from scipy.stats import fisher_exact
from tqdm.autonotebook import tqdm


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


def iter_contingency_tables(vals1, vals2, iter_values=[], min_count=None):

    assert is_listy(vals1),is_listy(vals2)
    s1,s2=pd.Series(vals1),pd.Series(vals2)
    counts1,counts2=s1.value_counts(), s2.value_counts()
    uniqvals = set(s1)|set(s2) if not iter_values else set(iter_values)

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
    count1=ctbl[0][0]
    count2=ctbl[0][1]
    support1=ctbl[0][0] + ctbl[1][0]
    support2=ctbl[0][1] + ctbl[1][1]
    perc1=count1/support1*100 if support1 else np.nan
    perc2=count2/support2*100 if support2 else np.nan
    perc_diff=perc2-perc1
    return {
        'count_L':count1,
        'count_R':count2,
        'perc_L':perc1,
        'perc_R':perc2,
        'perc_L->R':perc_diff,
    }



def quicklook_diffs(sL, sR):    
    df = pd.DataFrame([sL, sR], index=['L','R']).T
    df['L->R'] = df['R'] - df['L']
    df = df.round().astype(int)
    df = df[df['L->R']!=0]
    return df.T.rename_axis('LR')




def zfy(series):
    s=pd.Series(series).replace([np.inf, -np.inf], np.nan).dropna()
    if not len(s): return np.nan
    return (s - s.mean()) / s.std()


def filter_signif(df, p_col=None, min_p=MIN_P):
    if p_col is None: pcol=first([c for c in df if c=='pvalue' or c.endswith('_p')])
    if not pcol: return df
    return df[df[pcol] <= min_p]



def measure_dists(
        series1, 
        series2, 
        methods = [
            'braycurtis', 
            'canberra', 
            'chebyshev', 
            'cityblock', 
            'correlation', 
            'cosine', 
            'euclidean', 
            'jensenshannon', 
            'minkowski', 
        ],
        series_name='dists',
        calc = ['median']
        ):
    from scipy.spatial import distance
    a=pd.Series(series1).values
    b=pd.Series(series2).values
    o=pd.Series({fname:getattr(distance,fname)(a,b) for fname in methods}, name=series_name)
    for fname in calc: o[fname]=o.agg(fname)
    return o



def geodist(latlon1, latlon2, unit='km'):
    from geopy.distance import distance
    import numpy as np
    try:
        dist = distance(latlon1, latlon2)
        return getattr(dist,unit)
    except Exception:
        return np.nan
    