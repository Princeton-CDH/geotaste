from geotaste2.queries import *

def test_filter_query_str_series():
    assert filter_query_str_series('year', [1899,1900,1901,1902]) == '1899 <= year <= 1902'

    assert filter_query_str_series('year', [1899,1900,1901,1902]) == '1899 <= year <= 1902'

