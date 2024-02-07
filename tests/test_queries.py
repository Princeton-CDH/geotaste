import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from geotaste.queries import *
from pandas.testing import assert_frame_equal
dfeg = pd.DataFrame([{'group':'shoe', 'part':'foot'}, {'group':'shoe', 'part':'toe'}, {'group':'hat', 'part':'head'}, {'group':'desk', 'part':''}, {'group':'shoe', 'part':''}])


def test_filter_query_str_series():
    assert filter_query_str_series('year', [1899,1900,1901,1902]) == '(1899 <= year <= 1902)'

    assert filter_query_str_series('year', [1899,1900,1901,1902]) == '(1899 <= year <= 1902)'

    assert filter_query_str_series('gender',['Nonbinary','Female'],maxlen=2) == '((gender == "Nonbinary") or (gender == "Female"))'

    assert filter_query_str_series('gender',['Nonbinary','Female','Male'],maxlen=2) == '@overlaps(gender, ["Nonbinary", "Female", "Male"])'

    assert filter_query_str_series('gender',['Nonbinary','Female','Male'],maxlen=3) == """((gender == "Nonbinary") or (gender == "Female") or (gender == "Male"))"""

    assert filter_query_str_series('gender',['Nonbinary','Female','Male'],maxlen=3,plural_cols=['gender']) == '@overlaps(gender, ["Nonbinary", "Female", "Male"])'

    assert '"Nonbinary", "Female", or "Male"' in filter_query_str_series('gender',['Nonbinary','Female','Male'],maxlen=3,plural_cols=['gender'],human=True)




def test_has_any_value_for():
    assert list(dfeg[has_any_value_for(dfeg.part)].group) == ['shoe','shoe','hat']



def test_group_has_any_value_for():
    assert list(dfeg[group_has_any_value_for(dfeg.group, dfeg.part)].group) == ['shoe','shoe','hat','shoe']
    


def test_group_contains():
    df = dfeg.iloc[:3]
    assert list(group_contains(df.group, df.part, ['head'])) == [False,False,True]
    assert list(group_contains(df.group, df.part, ['toe'])) == [True,True,False]
    assert list(group_contains(df.group, df.part, ['foot'])) == [True,True,False]
    assert list(group_contains(df.group, df.part, ['xxx'])) == [False,False,False]

    df = dfeg.iloc[:4]
    assert list(group_contains(df.group, df.part, ['head'], allow_none=True)) == [False,False,True,None]
    assert list(group_contains(df.group, df.part, ['head'], allow_none=False)) == [False,False,True,False]

    assert list(df[group_contains_other(df.group, df.part, 'head')].group) == ['shoe','shoe']
    assert list(df[group_always_contains(df.group, df.part, 'head')].group) == ['hat']
    return list(df[group_never_contains(df.group, df.part, 'head')].group) == ['shoe','shoe']
    # assert list(df[group_contains_other(df.group, df.part, 'head')].group) == ['hat']


#) == [False,False,True,False]
    