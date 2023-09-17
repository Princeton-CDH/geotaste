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
    
def get_dist_from_SCO(lat,lon):
    return geodist((lat,lon), LATLON_SCO)






####

def describe_arronds(df_arronds, min_p=None, p_col=None):
    signif_df = filter_signif(df_arronds)

    if len(signif_df): 
        signif_df['odds_ratio'] = signif_df['odds_ratio'].replace(np.inf, np.nan)
        signif_df = signif_df[signif_df.odds_ratio.apply(is_numeric) & (~signif_df.odds_ratio.isna()) & (signif_df.odds_ratio!=0)]

    desc_top = f'''Comparing where members from Filter 1 and Filter 2 lived produces **{len(signif_df)}** statistically significant arrondissement.'''
    
    display(signif_df)


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
    # return f'* **{ratio:.1f}x** more likely to live in the **{astr}** ({pL:.1f}% = {cL:.0f}/{cL2:.0f} vs. {pR:.1f}% = {cR:.0f}/{cR2:.0f})'
    return f'* **{ratio:.1f}x** more likely to live in the **{astr}** ({pL:.2f}% vs. {pR:.2f}%, or {cL2:.0f} or {cL:,.0f} vs. {cR2:.0f} of {cR:,.0f})'

def describe_arronds_LR(signif_df, side='left'):
    descs=['',f'The {side.title()} Group is...']
    dfx=signif_df.reset_index().sort_values('odds_ratio', ascending=side!='left')
    for _,row in dfx.iterrows():
        descs.append(describe_arronds_row(row,side=side))
    return '\n'.join(descs)




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
        only_signif=True,
        round=4,
        min_count=1,
        min_sum=10,
        drop_duplicates=[],
        drop_empty=True
        ):
        
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
    # statcols=['col','col_val','count_sum','count_min','count_L','count_R','perc_L','perc_R','perc_L->R','odds_ratio','fisher_exact','fisher_exact_p']
    prefcols=['col','col_val','comparison_scale','odds_ratio','perc_L','perc_R','count_L','count_R']
    cols = prefcols + [c for c in alldf if c not in set(prefcols)]
    alldf=alldf[cols].sort_values('fisher_exact',ascending=False)
    sigdf=alldf.query('fisher_exact_p<=0.05')

    return (sigdf if only_signif else alldf).round(round)




def describe_comparison(comparison_df, lim=10, min_fac=None):
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
             orow=f'''* *{row.odds_ratio_pos:.2f}x* likelier for {row.col.replace("_id","").replace("_"," ").title()} to be **{row.col_val}** {pstr}
    * ({pL:.1f}% \[1] vs. {pR:.1f}% \[2], or {cL:.0f}/{tL:,.0f} \[1] vs. {cR:.0f}/{tR:,.0f} \[2] {row.comparison_scale.replace("_id","")}s)
'''
             o.append(orow)
             if lim and len(o)>=lim: break
        return o
    
    return get_list_desc(L), get_list_desc(R)

    
    
    



#@TODO: PARIS FILTER
def prune_when_dwelling_matches(df):
    df_nonevent, df_event=df[df.event==''],df[df.event!='']
    
    # anyone's ok if they're not an event
    numpossd = {ii:np.nan for ii in df.index}
    matchtyped={
        **{ii:'NA' for ii in df_nonevent.index},
        **{ii:'?' for ii in df_event.index}
    }
    matchfoundd={ii:None for ii in df.index}
    excludedd={ii:False for ii in df.index}


    def declare_impossible(xdf):
        # but declare them impossible to match to a dwelling
        for ii in xdf.index:
            matchtyped[ii]='Impossible'
            numpossd[ii]=0
            matchfoundd[ii]=False
            excludedd[ii]=True

    def declare_exact_match(xdf):
        for ii in xdf.index:
            matchtyped[ii]='Exact'
            matchfoundd[ii]=True
            numpossd[ii]=len(xdf)

    def declare_exact_miss(xdf):
        logger.trace(f'for event {e}, a certain match was found, with {len(xdf)} possibilities')
        for ii in xdf.index: 
            matchtyped[ii]='Exact (excl.)'
            excludedd[ii]=True
            matchfoundd[ii]=False

    def declare_ambiguous(xdf, caveats=[]):
        for ii in xdf.index: 
            probtype = 'Colens' if not len(xdf[xdf.dwelling_start!='']) else 'Raphael'
            mt=f'Ambiguous ({probtype})' if len(xdf)>1 else 'Singular'
            # if caveats: mt+=f' ({", ".join(caveats)})'
            matchtyped[ii]=mt
            matchfoundd[ii]=True
            numpossd[ii]=len(xdf)

    def find_exact_matches(xdf):
        erow=xdf.iloc[0]
        e1,e2=erow.event_start,erow.event_end
        match = xdf[[
            (is_fuzzy_date_seq(d1,e1,d2) or is_fuzzy_date_seq(d1,e2,d2))
            for (d1,d2) in zip(xdf.dwelling_start, xdf.dwelling_end)
        ]]
        logger.trace(f'found {len(match)} exact matches for {(e1, e2)} with options {list(zip(xdf.dwelling_start, xdf.dwelling_end))}')
        return match

    def declare_heuristic_miss(xdf, htype=''):
        for ii in xdf.index: 
            matchtyped[ii]=f'Heuristic (excl.{" by "+htype if htype else ""})'
            matchfoundd[ii]=False
            excludedd[ii]=True


    
    # for every event...
    for e,edf in tqdm(df_event.groupby('event'), total=df_event.event.nunique(), desc='Locating events'):
        logger.trace(f'event: {e}, with {len(edf)} dwelling possibilities')
        ## if there are no dwellings at all...
        nadf=edf[edf.dwelling=='']
        declare_impossible(nadf)

        edf=edf[edf.dwelling!=''].drop_duplicates('dwelling')
        if not len(edf):
            logger.trace(f'for event {e}, no dwelling possibilities because empty dwellings')
            continue
    
        # if certainty is possible, i.e. we have dwelling records with start and end dates...
        edf_certain = edf.query('dwelling_start!="" & dwelling_end!=""')
        if len(edf_certain):
            logger.trace(f'for event {e}, certainty is possible, with {len(edf_certain)} possibilities')
            # is there a match? a point where start or end of event is within range of dwelling start or end?
            edf_match = find_exact_matches(edf_certain)
            # if so, then add indices only for the match, not the other rows
            if len(edf_match):
                logger.trace(f'for event {e}, a certain match was found, with {len(edf_match)} possibilities')
                declare_exact_match(edf_match)
                declare_exact_miss(edf[~edf.index.isin(edf_match.index)])
                continue

        # try dispreferred caveats
        caveats=[]
        edf0 = edf
        edf = edf[~edf.dwelling_address.isin(DISPREFERRED_ADDRESSES)]
        if not len(edf):
            logger.trace(f'for event {e}, only a dispreferred address remained; allowing')
            edf=edf0
        elif len(edf)!=len(edf0):
            declare_heuristic_miss(edf0[~edf0.index.isin(edf.index)], htype='dispref')
            caveats.append('-dispref')

        # try distance caveat
        edf0 = edf
        edf = edf[[get_dist_from_SCO(lat,lon)<50 for lat,lon in zip(edf.lat, edf.lon)]]
        if not len(edf):
            logger.trace(f'for event {e}, only non-Parisian places remaining; allowing')
            edf=edf0
        elif len(edf)!=len(edf0):
            declare_heuristic_miss(edf0[~edf0.index.isin(edf.index)], htype='distance')
            caveats.append('-distance')

        # otherwise, declare ambiguous?
        logger.trace(f'for event {e}, still no matches found. using all {len(edf)} possible indices')
        declare_ambiguous(edf,caveats=caveats)
        
    # add to dataframe a few stats on the dwelling matches
    df['dwelling_matchfound'] = matchfoundd
    df['dwelling_matchtype'] = matchtyped
    df['dwelling_numposs'] = numpossd
    df['dwelling_excluded'] = excludedd
    df['dwelling_likelihood'] = 1/df['dwelling_numposs']

    # return only ok rows
    return df.loc[~df.dwelling_excluded]