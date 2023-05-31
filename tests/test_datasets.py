# code
import sys; sys.path.insert(0,'..')
from geotaste.datasets import *
import random,tempfile


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
        assert type(dset._data) is pd.DataFrame
        assert type(dset.data) is pd.DataFrame
        assert len(dset.data) == numrows
        assert len(dset.data.columns) == numcols

        colsnow = ['a', 'b']
        dset.cols = colsnow
        assert len(dset._data.columns) == numcols
        assert len(dset.data.columns) == len(colsnow)




def test_members_dataset():
    obj = MembersDataset()
    df = obj.data
    assert 'James Joyce' in set(df.name)

    dfj = df[df.name=='James Joyce']
    assert set(dfj.index) == {'joyce-james'}

    for col in obj.cols_sep:
        assert {type(x) for x in df[col]} == {list}



def test_authors_dataset():
    obj = AuthorsDataset()
    df = obj.data
    assert 'James Joyce' in set(df.name)

