import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from geotaste.imports import *
import tempfile
from pandas.testing import assert_frame_equal

def biasedseries(bias_n=1, bias_fac=.5):
    if random.random()>bias_fac:
        return str(bias_n)
    else:
        return str(random.randint(1,10))


def test_analyze_contingency_tables():
    cols=['count_sum', 'count_min', 'count_L', 'count_R', 'perc_L', 'perc_R', 'perc_L->R', 'odds_ratio', 'fisher_exact', 'fisher_exact_p']
    
    # Create mock inputs
    vals1 = pd.Series([biasedseries(1) for _ in range(1000)], name='vals1')
    vals2 = pd.Series([biasedseries(2) for _ in range(1000)], name='vals2')

    # Define the minimum p-value threshold
    MIN_P = 0.05

    # Call the function with the mock inputs
    output_df = analyze_contingency_tables(vals1, vals2, min_p=MIN_P, signif=True)
    print(list(output_df.columns))

    # Check that the output DataFrame has the correct columns
    assert set(output_df.columns) == set(cols), f"Output DataFrame should contain columns for {cols}"

    # Check that the DataFrame is sorted in ascending order by 'odds_ratio'
    assert (output_df['odds_ratio'].sort_values() == output_df['odds_ratio']).all(), "Output DataFrame should be sorted in ascending order by odds_ratio"

    # Check that the DataFrame contains only rows with 'fisher_exact_p' <= MIN_P
    assert (output_df['fisher_exact_p'] <= MIN_P).all(), "Output DataFrame should only contain rows with 'fisher_exact_p' <= MIN_P"

    # '1' should be biased 1
    r1=output_df.loc['1']
    r2=output_df.loc['2']
    assert r1.perc_L > r1.perc_R
    assert r2.perc_L < r2.perc_R
    assert r1.fisher_exact_p < .05
    assert r2.fisher_exact_p < .05


def test_iter_contingency_tables():
    # Define the inputs
    vals1 = ['a', 'b', 'c', 'a', 'b', 'c']
    vals2 = ['b', 'c', 'd', 'b', 'c', 'd']

    # The expected output is a dictionary with unique values from input lists as keys
    # and corresponding contingency tables as values
    expected_output = {
        'a': ((2, 0), (4, 6)),
        'b': ((2, 2), (4, 4)),
        'c': ((2, 2), (4, 4)),
        'd': ((0, 2), (6, 4))
    }

    # Call the function and transform output to dictionary for easy comparison
    output = dict(list(iter_contingency_tables(vals1, vals2)))

    # Assert the output matches the expected
    assert output == expected_output, \
        f"Expected {expected_output}, but got {output}"



def test_table_info():
    def roundd(d):
        return {k:round(v) for k,v in d.items()}

    # Test 1: Normal Case
    assert roundd(table_info([[10, 20], [30, 40]])) == roundd({
        'count_sum': 30,
        'count_min': 10,
        'count_L': 10,
        'count_R': 20,
        'perc_L': 25.0,
        'perc_R': 33.33333333333333,
        'perc_L->R': 8.333333333333329
    })

    # Test 2: When count1 > count2
    assert roundd(table_info([[15, 5], [10, 20]])) == roundd({
        'count_sum': 20,
        'count_min': 5,
        'count_L': 15,
        'count_R': 5,
        'perc_L': 60.0,
        'perc_R': 20.0,
        'perc_L->R': -40.0
    })

    # Test 3: When count1 < count2
    assert roundd(table_info([[5, 15], [10, 20]])) == roundd({
        'count_sum': 20,
        'count_min': 5,
        'count_L': 5,
        'count_R': 15,
        'perc_L': 33.33333333333333,
        'perc_R': 42.857142857142854,
        'perc_L->R': 9.523809523809518
    })


def test_filter_signif():
    # Create a DataFrame for testing 
    df = pd.DataFrame({
        'A': [1, 2, 3, 4],
        'B': ['a', 'b', 'c', 'd'],
        'pvalue': [0.05, 0.1, 0.15, 0.2]
    })

    # Test 1: Normal case
    expected_df1 = pd.DataFrame({
        'A': [1, 2],
        'B': ['a', 'b'],
        'pvalue': [0.05, 0.1]
    })
    assert filter_signif(df, min_p=0.1).equals(expected_df1)

    # Test 2: No p-value column is specified
    expected_df2 = pd.DataFrame({
        'A': [1, 2],
        'B': ['a', 'b'],
        'pvalue': [0.05, 0.1]
    })
    assert filter_signif(df, min_p=0.1).equals(expected_df2)

    # Test 3: p-value column is specified
    expected_df3 = pd.DataFrame({
        'A': [1, 2],
        'B': ['a', 'b'],
        'pvalue': [0.05, 0.1]
    })
    assert filter_signif(df, p_col='pvalue', min_p=0.1).equals(expected_df3)

    # Test 4: Test with a dataframe has no column named 'pvalue' or ending with '_p'
    df_no_p_col = pd.DataFrame({
        'A': [1, 2, 3, 4],
        'B': ['a', 'b', 'c', 'd'],
    })
    assert filter_signif(df_no_p_col, min_p=0.1).equals(df_no_p_col)

    # Test 5: Test with min_p specified as None
    assert filter_signif(df, min_p=None).equals(df)



def test_geodist():
    # Test with valid inputs and default unit 'km'.
    assert abs(geodist((48.8566, 2.3522), LATLON_SCO)) > 1, "Test case 1 failed"
    # Test with the same location (distance should be 0).
    assert geodist((48.8566, 2.3522), (48.8566, 2.3522)) == 0, "Test case 2 failed"
    # Test with invalid inputs (longitude > 180).
    assert np.isnan(geodist((50, 200), (50, 50))), "Test case 3 failed"

import pandas as pd
import numpy as np

def test_get_distinctive_qual_vals():
    '''
    A simple test function for get_distinctive_qual_vals().
    '''
    # Prepare inputs
    dfL = CombinedFigureFactory({'member_gender':['Female']}).data
    dfR = CombinedFigureFactory({'member_gender':['Male']}).data

    # Run the function
    output = get_distinctive_qual_vals(dfL, dfR, cols=[
            'member_title', 
            'member_nationalities'
        ])
    print(output.columns)
    print(output)

    # Check the outputs
    assert isinstance(output, pd.DataFrame), "Output is not a DataFrame."

    columns = ['col','col_val','comparison_scale','odds_ratio','perc_L','perc_R','count_L','count_R']
    assert all(col in output.columns for col in columns), "Output DataFrame is missing expected columns."

    # Check the 'col' and 'col_val' column have expected values
    assert output['col'].nunique() == 2, "'col' column does not have 2 unique values."

    # Check the 'odds_ratio' column values
    assert all(np.isnan(output['odds_ratio']) == False), "'odds_ratio' column contains NaN values."

    # Check the 'perc_L' and 'perc_R' column values
    assert all(output['perc_L'] != 0), "'perc_L' column values are all 0."
    assert all(output['perc_R'] != 0), "'perc_R' column values are all 0."

    # Check the 'count_L' and 'count_R' column values
    assert all(output['count_L'] != 0.0), "'count_L' column values are all 0.0."
    assert all(output['count_R'] != 0.0), "'count_R' column values are all 0.0."

    output2 = get_distinctive_qual_vals(dfL, dfR, cols=['member_title', 'member_nationalities'],drop_duplicates='member')
    output3 = get_distinctive_qual_vals(dfL, dfR, cols=['member_title', 'member_nationalities'],drop_duplicates=['member'])
    assert_frame_equal(output2, output3)
    assert len(output2)<len(output)

    # Run the function
    output4 = get_distinctive_qual_vals(dfL, dfR, cols=[
        'member_title', 
        'member_nationalities',
    ], maxcats=2)
    assert len(output4)==0




def test_describe_comparison():
    ff=ComparisonFigureFactory({'member_gender':['Male']}, {'member_gender':['Female']})
    df=ff.compare(cols=['member_title'])
    L,R=describe_comparison(df)
    assert L and R, "no result"
    assert '**M.**' in L[0], 'not expected result'
    assert '**Mme**' in R[0], 'not expected result'


