import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from geotaste.utils import *
import tempfile
from pandas.testing import assert_frame_equal


def test_hasone():
    assert hasone([1, 2, 3], [3, 4, 5]) == True
    assert hasone([1, 2, 3], [4, 5, 6]) == False

def test_isin():
    assert isin(1, [1, 2, 3]) == True
    assert isin(4, [1, 2, 3]) == False

def test_isin_or_hasone():
    assert isin_or_hasone(1, [1, 2, 3]) == True
    assert isin_or_hasone([1, 2, 3], [3, 4, 5]) == True
    assert isin_or_hasone(4, [1, 2, 3]) == False
    assert isin_or_hasone(4, 4) == True
    assert isin_or_hasone(4, 5) == False


def test_to_set():
    assert to_set(1) == {1}
    assert to_set([1, 2, 3]) == {1, 2, 3}

def test_overlaps():
    series = pd.Series([1, 2, 3, 4, 5])
    assert (overlaps(series, [3, 4, 5]) == pd.Series([False, False, True, True, True])).all()

def test_is_numeric():
    assert is_numeric(1) == True
    assert is_numeric("hello") == False

def test_is_listy():
    assert is_listy([1, 2, 3]) == True
    assert is_listy((1, 2, 3)) == True
    assert is_listy(pd.Series([1, 2, 3])) == True
    assert is_listy(1) == False

def test_ensure_dict():
    assert ensure_dict(None) == {}
    assert ensure_dict({'a': 1, 'b': 2}) == {'a': 1, 'b': 2}
    assert ensure_dict([('a', 1), ('b', 2)]) == {'a': 1, 'b': 2}

def test_find_plural_cols():
    df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [[1, 2], [3, 4], [5, 6]]})
    assert find_plural_cols(df) == ['col2']

def test_first():
    assert first([1, 2, 3]) == 1
    assert first([1, 2, 3], default=0) == 1
    assert first([], default=0) == 0

def test_flatten_list():
    assert flatten_list([1, 2, [3, 4], [5, [6, 7]]]) == [1, 2, 3, 4, 5, 6, 7]
    assert flatten_list([[1, 2], [3, 4], [5, 6]]) == [1, 2, 3, 4, 5, 6]
    assert flatten_list([1, [2, [3, [4, [5]]]]]) == [1, 2, 3, 4, 5]

def test_flatten_series():
    s = pd.Series([1, [2, 3], 4])
    expected = pd.Series([1, 2, 3, 4], index=[0, 1, 1, 2])
    assert flatten_series(s).equals(expected)

def test_make_counts_df():
    series = pd.Series(['apple', 'banana', 'apple', 'orange', 'banana'], name='fruits')
    counts_df = make_counts_df(series)
    assert counts_df['fruits'].tolist() == ['apple', 'banana', 'orange']
    assert counts_df['count'].tolist() == [2, 2, 1]

def test_ordinal_str():
    assert ordinal_str(1) == "1st"
    assert ordinal_str(2) == "2nd"
    assert ordinal_str(3) == "3rd"
    assert ordinal_str(4) == "4th"
    assert ordinal_str(10) == "10th"
    assert ordinal_str(11) == "11th"
    assert ordinal_str(12) == "12th"
    assert ordinal_str(13) == "13th"

def test_force_int():
    assert force_int(5) == 5
    assert force_int("10") == 10
    assert force_int("abc", errors=-1) == -1
    assert force_int("5.5", errors=-1) == -1


## Tests deprecated behavior
# @TODO: update

def test_combine_LR_df():
    dfL = pd.DataFrame({'A': [1, 2, 3]}, index=[0, 1, 2])
    dfR = pd.DataFrame({'B': [4, 5, 6]}, index=[3, 4, 5])
    odf = combine_LR_df(dfL, dfR, colname='colname', colval_L='colL', colval_R='colR')
    assert len(odf) == len(dfL) + len(dfR)
    assert set(odf['colname']) == {'colL','colR'}
    assert list(odf.index) == [0, 1, 2, 3, 4, 5]





def test_serialize():
    d = {'name': 'John', 'age': 30, 'city': 'New York'}
    serialized = serialize(d)
    assert serialized == '{"age":30,"city":"New York","name":"John"}'

def test_unserialize():
    d_str = '{"age":30,"city":"New York","name":"John"}'
    unserialized = unserialize(d_str)
    assert unserialized == {'name': 'John', 'age': 30, 'city': 'New York'}

def test_serializing():
    d = {'name': 'John', 'age': 30, 'city': 'New York'}
    assert unserialize(serialize(d)) == d
    

def test_selectrename_df():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
    col2col = {'A': 'X', 'B': 'Y'}
    assert selectrename_df(df, col2col).equals(pd.DataFrame({'X': [1, 2, 3], 'Y': [4, 5, 6]}))

def test_qualquant_series():
    assert (qualquant_series([1, 2, 3, 4, 5], True) == pd.Series([1, 2, 3, 4, 5])).all()
    assert (qualquant_series(["1", "2", "3", "4", "5"], False) == pd.Series(["1", "2", "3", "4", "5"])).all()

def test_uid():
    assert len(uid(8)) == 8
    assert len(uid()) == 10  # default length is 10

def test_Logwatch():
    import time
    logger = Logwatch(level='debug')
    assert logger.level == 'debug'

    with Logwatch() as l:
        time.sleep(1)
    assert l.duration >= 1


def test_is_range_of_ints():
    assert is_range_of_ints([1,2,4]) == False
    assert is_range_of_ints([1,2,3,4]) == True
    assert is_range_of_ints([1,2,3.0,4.000]) == True
    assert is_range_of_ints([-1,0,1,2,3.0,4.000]) == True
    assert is_range_of_ints([1,2,'three']) == False
    assert is_range_of_ints(object) == False



def test_delist_df():
    # create a sample dataframe for testing
    df1 = pd.DataFrame({
        'A': [[1, 2, 3], [4, 5, 6]],
        'B': [2.666666, 3.777777],
        'C': ['non-changed item', 'another non-changed item']
    })

    # expected output from delist_df function
    expected_df1 = pd.DataFrame({
        'A': ['1 2 3', '4 5 6'],
        'B': [2.67, 3.78],
        'C': ['non-changed item', 'another non-changed item']
    })

    # assert that the function works as expected
    assert_frame_equal(delist_df(df1), expected_df1)

    # test with another separator
    df2 = pd.DataFrame({
        'A': [[1, 2, 3], [4, 5, 6]],
        'B': [2.666666, 3.777777],
        'C': ['non-changed item', 'another non-changed item']
    })

    # expected output from delist_df function
    expected_df2 = pd.DataFrame({
        'A': ['1-2-3', '4-5-6'],
        'B': [2.67, 3.78],
        'C': ['non-changed item', 'another non-changed item']
    })

    # assert that the function works as expected
    assert_frame_equal(delist_df(df2, sep='-'), expected_df2)

    # test with Nan values
    df3 = pd.DataFrame({
        'A': [[1, np.nan, 3], [4, np.nan, 6]],
        'B': [2.666666, np.nan],
        'C': ['non-changed item', np.nan]
    })

    # expected output from delist_df function
    expected_df3 = pd.DataFrame({
        'A': ['1 nan 3', '4 nan 6'],
        'B': [2.67, np.nan],
        'C': ['non-changed item', np.nan]
    })

    # assert that the function works as expected
    assert_frame_equal(delist_df(df3), expected_df3)



def test_fuzzydates():
    assert date_fuzzily_precedes('1750', '1750-12-12') == False
    assert date_fuzzily_follows('1750', '1750-12-12') == False
    assert date_fuzzily_follows('1750', '1751-12-12') == False
    assert date_fuzzily_follows('1750', '1749-12-12') == True
    assert date_fuzzily_precedes('1799-10-01', '1800') == True


def test_ensure_int():
    assert ensure_int(1.0) == 1
    assert ensure_int(1) == 1
    assert ensure_int('1') == 1
    assert ensure_int('x', return_orig=False, default=None) == None
    assert ensure_int('x', return_orig=False, default=1) == 1
    assert ensure_int('x', return_orig=True) == 'x'

def test_ensure_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        odir=os.path.join(tmpdir,'tmpxxx')
        outfn=os.path.join(odir,'out.txt')
        ensure_dir(outfn)
        assert os.path.exists(odir)
        assert not os.path.exists(outfn)
        with open(outfn,'w') as of: of.write('testing')
        assert os.path.exists(outfn)


def test_oxfordcomma():
    # Test with three elements in the list
    assert oxfordcomma(['apple', 'banana', 'orange']) == "'apple', 'banana', and 'orange'"
    
    # Test with two elements in the list
    assert oxfordcomma(['apple', 'banana']) == "'apple' and 'banana'"
    
    # Test with one element in the list
    assert oxfordcomma(['apple']) == "'apple'"
    
    # Test with an number elements in the list
    assert oxfordcomma([1, 2, 3]) == "1, 2, and 3"

    assert oxfordcomma(['1', '2', '3']) == "'1', '2', and '3'"
    
    # Test with different op (conjunction) value
    assert oxfordcomma(['apple', 'banana', 'orange'], op='or') == "'apple', 'banana', or 'orange'"
    
    # Test with repr function to represent each element as a string
    assert oxfordcomma([1, 2, 3], repr=str) == "1, 2, and 3"
    assert oxfordcomma(['1', '2', '3'], repr=str) == "1, 2, and 3"
    assert oxfordcomma(['apple', 'banana', 'orange'], repr=str) == "apple, banana, and orange"


def test_read_config_json():
    d1=read_config_json(PATH_CONFIG_DEFAULT)
    assert type(d1)==dict and d1
    with tempfile.TemporaryDirectory() as tdir:        
        try:
            read_config_json(os.path.join(tdir,'nonexistentfile.json'))
            assert False, 'ought to throw exception for reading unknown json file'
        except Exception:
            assert True, 'success'