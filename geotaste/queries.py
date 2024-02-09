from .imports import *


def filter_df(
    df: pd.DataFrame,
    filter_data={},
    groupby: Optional[str] = None,
    fname: str = 'contains',
    operator: str = 'and',
    return_query: bool = False,
) -> pd.DataFrame:
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
    qstr = (
        format_query(
            filter_data,
            groupby=groupby,
            fname=fname,
            operator=operator,
            human=False,
        )
        if type(filter_data) != str
        else filter_data
    )

    # query and return
    if qstr:
        logger.debug(f'Querying: {qstr}')
    odf = df.query(qstr) if qstr else df
    return (qstr, odf) if return_query else odf


### BY ROW


def has_any_value(series):
    return series.apply(is_not_null)


def match_series_values(series, matching):
    if is_null(matching):
        return series
    vals_set = to_set(matching)
    series_set = series.apply(to_set)
    return series_set.apply(
        lambda xset: None if not xset else bool(xset & vals_set)
    )


def contains(
    series: pd.Series, matching: Iterable, allow_none=False
) -> pd.Series:
    """
    Check if each element in the series overlaps with the given values.

    Parameters:
    - series (pd.Series): The series to check for overlaps.
    - matching (Iterable): The values to check for overlap with the series elements.
    - allow_none (bool): Flag indicating whether to allow None values in the series. Default is False.
    - is_neg (bool): Flag indicating whether to perform negation of the overlap check. Default is None.

    Returns:
    - pd.Series: A series of boolean values indicating whether each element in the series overlaps with the given values.
    """
    res = match_series_values(series, matching)
    return res if allow_none else res.apply(lambda x: x is True)


def contains_other(
    series: pd.Series, matching: Iterable, allow_none=False
) -> pd.Series:
    res = match_series_values(series, matching)
    return res if allow_none else res.apply(lambda x: x is False)


### GROUPS


def group_has_any_value(groups, series):
    minidf = pd.DataFrame({'grp': groups, 'val': series})
    group_to_truth = {
        grpname: any(has_any_value(grpdf.val))
        for grpname, grpdf in minidf.groupby('grp')
    }
    return pd.Series(
        (group_to_truth[g] for g in groups),
        index=series.index,
        name=series.name,
    )


def _group_contains(
    groups: pd.Series,
    series: pd.Series,
    matching: list,
    once_pos: bool = False,
    once_neg: bool = False,
    always_pos: bool = False,
    always_neg: bool = False,
    allow_none: bool = False,
) -> pd.Series:

    if is_null(matching):
        return pd.Series(
            (True for _ in series), index=series.index, name=series.name
        )
    if is_null(groups):
        groups = series.index
    assert len(series) == len(groups)
    minidf = pd.DataFrame({'grp': groups, 'val': series})

    def get_grp_truth(s, grpname):
        res = set(contains(s, matching, allow_none=True))
        if res == {None}:
            return None
        if not res:
            return None
        if once_pos:
            return any(res)
        if once_neg:
            return False in res
        if always_neg:
            return False in res and not True in res
        if always_pos:
            return True in res and not False in res
        raise Exception('?')

    group_to_truth = {
        grpname: get_grp_truth(grpdf.val, grpname)
        for grpname, grpdf in minidf.groupby('grp')
    }
    res = pd.Series(
        (group_to_truth[g] for g in groups),
        index=series.index,
        name=series.name,
    )
    return res if allow_none else res.apply(bool)


def group_contains(
    groups: pd.Series,
    series: pd.Series,
    matching: list,
    allow_none: bool = False,
) -> pd.Series:

    return _group_contains(
        groups=groups,
        series=series,
        matching=matching,
        once_pos=True,
        allow_none=allow_none,
    )


def group_contains_other(
    groups: pd.Series,
    series: pd.Series,
    matching: list,
    allow_none: bool = False,
) -> pd.Series:

    return _group_contains(
        groups=groups,
        series=series,
        matching=matching,
        once_neg=True,
        allow_none=allow_none,
    )


def group_never_contains(
    groups: pd.Series,
    series: pd.Series,
    matching: list,
    allow_none: bool = False,
) -> pd.Series:

    return _group_contains(
        groups=groups,
        series=series,
        matching=matching,
        always_neg=True,
        allow_none=allow_none,
    )


def group_always_contains(
    groups: pd.Series,
    series: pd.Series,
    matching: list,
    allow_none: bool = False,
) -> pd.Series:

    return _group_contains(
        groups=groups,
        series=series,
        matching=matching,
        always_pos=True,
        allow_none=allow_none,
    )
