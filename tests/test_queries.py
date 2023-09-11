import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from geotaste.queries import *

def test_filter_query_str_series():
    assert filter_query_str_series('year', [1899,1900,1901,1902]) == '(1899 <= year <= 1902)'

    assert filter_query_str_series('year', [1899,1900,1901,1902]) == '(1899 <= year <= 1902)'

    assert filter_query_str_series('gender',['Nonbinary','Female'],maxlen=2) == '((gender == "Nonbinary") or (gender == "Female"))'

    assert filter_query_str_series('gender',['Nonbinary','Female','Male'],maxlen=2) == '@overlaps(gender, ["Nonbinary", "Female", "Male"])'

    assert filter_query_str_series('gender',['Nonbinary','Female','Male'],maxlen=3) == """((gender == "Nonbinary") or (gender == "Female") or (gender == "Male"))"""

    assert filter_query_str_series('gender',['Nonbinary','Female','Male'],maxlen=3,plural_cols=['gender']) == '@overlaps(gender, ["Nonbinary", "Female", "Male"])'

