import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# code
from geotaste.datasets import *
import random,tempfile
from pandas.testing import assert_frame_equal

def test_dataset():
    with tempfile.TemporaryDirectory() as tdir:
        numrows = 10

        df = pd.DataFrame(
            {'a':random.random(), 'b':random.random(), 'c':random.random()}
            for n in range(numrows)
        )
        numcols = len(df.columns)
        ofn=os.path.join(tdir,'data.csv')
        df.to_csv(ofn, index=False)

        # open dataset
        dset = Dataset(ofn)

        assert dset.path == ofn
        assert type(dset.data) is pd.DataFrame
        assert len(dset.data) == numrows
        assert len(dset.data.columns) == numcols



def _test_dset(dset):
    df=dset.data
    def colx(x): 
        try:
            return dset._cols_rename.get(x,x)
        except AttributeError:
            return dset.cols_rename.get(x,x)
        
    for col in dset.cols_sep:
        if colx(col) in set(df.columns):
            assert {type(x) for x in df[colx(col)]} == {list}

    for col in dset.cols_q:
        if colx(col) in set(df.columns):
            assert not {type(x) for x in df[colx(col)]} - {list, float, int}
    
    newcols = set(dset._cols_rename.values() if hasattr(dset,'_cols_rename') else dset.cols_rename.values())
    oldcols = set(dset._cols_rename.keys() if hasattr(dset,'_cols_rename') else dset.cols_rename.keys()) - newcols

    assert not (oldcols & set(df.columns))
    assert not (newcols - set(df.columns))

    assert list(df.columns)[:len(dset.cols_pref)] == [colx(x) for x in dset.cols_pref]





def test_landmarks_dataset():
    dset = LandmarksDataset()
    _test_dset(dset)

    assert 'arrond_id' in set(dset.data.columns)
    assert 'tooltip' in set(dset.data.columns)
    assert dset.data.lat.dtype == np.float64
    assert dset.data.lon.dtype == np.float64

    assert 'Shakespeare and Company' in set(dset.data.landmark)
    assert 'American Hospital of Paris' in set(dset.data.landmark)

    assert dset.data.set_index('landmark').loc['American Hospital of Paris'].arrond_id == 'NA'
    assert dset.data.set_index('landmark').loc['Shakespeare and Company'].arrond_id == '6'

    dset1 = Landmarks()
    dset2 = Landmarks()
    assert dset1 is dset2
    assert dset1 is not dset
    assert_frame_equal(dset.data, dset1.data)

    


def test_members_dataset():
    dset = Members()
    _test_dset(dset)

    df = dset.data
    namecol = 'member_name'
    names = df[namecol]
    assert 'James Joyce' in set(names)

    dfj = df[df[namecol]=='James Joyce']
    assert set(dfj.member) == {'joyce-james'}



def test_books_dataset():
    dset = Books()
    _test_dset(dset)

def test_events_dataset():
    dset = Events()
    _test_dset(dset)



def test_combined_dataset():
    dset = Combined()
    _test_dset(dset)



def test_prune_when_dwelling_matches():
    with Logwatch('generating mini combined dataset'):
        df = CombinedDataset().gen(progress=False)

    dtypes = df.dwelling_matchtype.unique()
    assert set(dtypes) == {
        'NA', 'Singular', 'Ambiguous (Colens)', 'Exact', 'Ambiguous (Raphael)'
    }


    s=df.groupby('dwelling_matchtype').event.nunique().sort_values(ascending=False)
    index=list(s.index)
    assert index[-1] == 'NA'
    assert index[0] == 'Singular'
    assert s['Exact'] > 1000





