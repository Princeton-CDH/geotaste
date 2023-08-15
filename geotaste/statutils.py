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


def iter_contingency_tables(vals1:'Iterable', vals2:'Iterable', uniqvals:'Iterable'=[], min_count:int|None=None):
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
    if min_p is None: return df
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
    







####

def describe_arronds(df_arronds, min_p=None, p_col=None):
    signif_df = filter_signif(df_arronds)

    if len(signif_df): 
        signif_df['odds_ratio'] = signif_df['odds_ratio'].replace(np.inf, np.nan)
        signif_df = signif_df[signif_df.odds_ratio.apply(is_numeric) & (~signif_df.odds_ratio.isna()) & (signif_df.odds_ratio!=0)]

    desc_top = f'''Comparing where members from Filter 1 and Filter 2 lived produces **{len(signif_df)}** statistically significant arrondissement.'''
    
    signif_more_L=signif_df[signif_df.odds_ratio>1]
    signif_more_R=signif_df[signif_df.odds_ratio<1]

    desc_L=describe_arronds_LR(signif_more_L,side='left') if len(signif_more_L) else ''
    desc_R=describe_arronds_LR(signif_more_R,side='right') if len(signif_more_R) else ''

    return (desc_L,desc_R,desc_top)

def describe_arronds_row(row,side='left'):
    ratio = row.odds_ratio
    cL,cR,pL,pR=row.count_L,row.count_R,row.perc_L,row.perc_R
    if side=='right':
        if ratio == 0: ratio=np.nan
        ratio=1/ratio
        cL,cR=cR,cL
        pL,pR=pR,pL
    cL2 = cL*pR
    cR2 = cR*pR
    astr=ordinal_str(int(row.arrond_id))
    return f'* **{ratio:.1f}x** more likely to live in the **{astr}** ({pL:.1f}% = {cL:.0f}/{cL2:.0f} vs. {pR:.1f}% = {cR:.0f}/{cR2:.0f})'

def describe_arronds_LR(signif_df, side='left'):
    descs=['',f'The {side.title()} Group is...']
    dfx=signif_df.reset_index().sort_values('odds_ratio', ascending=side!='left')
    for _,row in dfx.iterrows():
        descs.append(describe_arronds_row(row,side=side))
    return '\n'.join(descs)

