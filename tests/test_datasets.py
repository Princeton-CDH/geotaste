import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# code
from geotaste.datasets import *
import random, tempfile
from pandas.testing import assert_frame_equal


def test_dataset():
    with tempfile.TemporaryDirectory() as tdir:
        numrows = 10

        df = pd.DataFrame(
            {'a': random.random(), 'b': random.random(), 'c': random.random()}
            for n in range(numrows)
        )
        numcols = len(df.columns)
        ofn = os.path.join(tdir, 'data.csv')
        df.to_csv(ofn, index=False)

        # open dataset
        dset = Dataset(ofn)

        assert dset.path == ofn
        assert type(dset.data) is pd.DataFrame
        assert len(dset.data) == numrows
        assert len(dset.data.columns) == numcols

        try:
            Dataset().read_df()
            assert False, 'ought not to be able to read'
        except Exception:
            assert True, 'exception ought to be called'

        try:
            Dataset(path=os.path.join(tdir, 'tmp2', 'file.txt')).read_df()
            assert False, 'ought not to be able to read'
        except Exception:
            assert True, 'exception ought to be called'

        try:
            Dataset(
                path=os.path.join(tdir, 'tmp3', 'file.csv'),
                url=URLS.get('landmarks'),
            ).read_df()
            assert False, 'ought not to be able to read'
        except Exception:
            assert True, 'exception ought to be called'


def _test_dset(dset):
    df = dset.data

    def colx(x):
        try:
            return dset._cols_rename.get(x, x)
        except AttributeError:
            return dset.cols_rename.get(x, x)

    for col in dset.cols_sep:
        if colx(col) in set(df.columns):
            assert {type(x) for x in df[colx(col)]} == {list}

    for col in dset.cols_q:
        if colx(col) in set(df.columns):
            assert not {type(x) for x in df[colx(col)]} - {list, float, int}

    newcols = set(
        dset._cols_rename.values()
        if hasattr(dset, '_cols_rename')
        else dset.cols_rename.values()
    )
    oldcols = (
        set(
            dset._cols_rename.keys()
            if hasattr(dset, '_cols_rename')
            else dset.cols_rename.keys()
        )
        - newcols
    )

    assert not (oldcols & set(df.columns))
    assert not (newcols - set(df.columns))

    assert list(df.columns)[: len(dset.cols_pref)] == [
        colx(x) for x in dset.cols_pref
    ]


def test_landmarks_dataset():
    dset = LandmarksDataset()
    _test_dset(dset)

    assert 'arrond_id' in set(dset.data.columns)
    assert 'tooltip' in set(dset.data.columns)
    assert dset.data.lat.dtype == np.float64
    assert dset.data.lon.dtype == np.float64

    assert 'Shakespeare and Company' in set(dset.data.landmark)
    assert 'American Hospital of Paris' in set(dset.data.landmark)

    assert (
        dset.data.set_index('landmark')
        .loc['American Hospital of Paris']
        .arrond_id
        == 'NA'
    )
    assert (
        dset.data.set_index('landmark')
        .loc['Shakespeare and Company']
        .arrond_id
        == '6'
    )

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

    dfj = df[df[namecol] == 'James Joyce']
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
    assert len(CombinedDataset().data)


def test_gen_combined_dataset():
    with Logwatch('generating mini combined dataset'):
        df = CombinedDataset().gen(progress=False, frac=0.1, save=False)

    dtypes = df.dwelling_matchtype.unique()
    assert set(dtypes) == {
        'NA',
        'Singular',
        'Ambiguous (Colens)',
        'Exact',
        'Ambiguous (Raphael)',
    }
    s = (
        df.groupby('dwelling_matchtype')
        .event.nunique()
        .sort_values(ascending=False)
    )
    index = list(s.index)
    assert index[-1] == 'NA'
    assert index[0] == 'Singular'
    assert s['Exact'] > 0


def test_gen_combined_dataset2():
    with tempfile.TemporaryDirectory() as tdir:
        dset1 = CombinedDataset()
        dset1.path = os.path.join(tdir, 'new.csv')

        dset2 = CombinedDataset()
        dset2.path = os.path.join(tdir, 'new2.csv')
        dset2.url = ''

        with Logwatch('downloading dataset for test2?') as lw1:
            dset1.data

        with Logwatch('generating dataset for test2?') as lw2:
            dset2.data

        assert lw2.duration > (
            lw1.duration * 2
        )  # ought to take at least twice as much time to gen than to download


def test_prune_when_dwelling_matches():
    mockdata = pd.DataFrame(
        [
            dict(
                event='E1',
                dwelling='D1',
                event_start='1920-01-24',
                event_end='1920-01-29',
                dwelling_start='1920-01-20',
                dwelling_end='1922-05-19',
            ),
            dict(
                event='E1',
                dwelling='D2',
                event_start='1920-01-24',
                event_end='1920-01-29',
                dwelling_start='1915-01-20',
                dwelling_end='1919-05-19',
            ),
        ]
    )

    resdf = prune_when_dwelling_matches(mockdata, progress=False)
    assert len(resdf) == 1
    assert resdf.iloc[0].dwelling_matchtype == 'Exact'
    assert resdf.iloc[0].dwelling_numposs == 1

    ## Test 2: event is 1920-01-24, dwelling starts 1920-01
    # we want: Exact, match

    mockdata = pd.DataFrame(
        [
            dict(
                event='E1',
                dwelling='D1',
                event_start='1920-01-24',
                event_end='1920-01-29',
                dwelling_start='1920-01',
                dwelling_end='1922-05',
                dwelling_address='21 Jump St',
                lat=LATLON_SCO[0] - 0.01,
                lon=LATLON_SCO[1] - 0.01,
            ),
            dict(
                event='E1',
                dwelling='D2',
                event_start='1920-01-24',
                event_end='1920-01-29',
                dwelling_start='1915-01',
                dwelling_end='1919-05',
                dwelling_address='22 Jump St',
                lat=LATLON_SCO[0] - 0.02,
                lon=LATLON_SCO[1] - 0.02,
            ),
        ]
    )

    resdf = prune_when_dwelling_matches(mockdata, progress=False)
    assert len(resdf) == 1
    assert resdf.iloc[0].dwelling_matchtype == 'Exact'
    assert resdf.iloc[0].dwelling_numposs == 1

    ## Test 3: If dwelling starts 1920-02, because end ends 1920-01-29, then this is not exact match; there is no exact match; therefore both returned as Ambiguous (Colens)
    mockdata = pd.DataFrame(
        [
            dict(
                event='E1',
                dwelling='D1',
                event_start='1920-01-24',
                event_end='1920-01-29',
                dwelling_start='1920-02',
                dwelling_end='1922-05',
                dwelling_address='21 Jump St',
                lat=LATLON_SCO[0] - 0.001,
                lon=LATLON_SCO[1] - 0.001,
            ),
            dict(
                event='E1',
                dwelling='D2',
                event_start='1920-01-24',
                event_end='1920-01-29',
                dwelling_start='1915-01',
                dwelling_end='1919-05',
                dwelling_address='22 Jump St',
                lat=LATLON_SCO[0] - 0.002,
                lon=LATLON_SCO[1] - 0.002,
            ),
        ]
    )

    resdf = prune_when_dwelling_matches(mockdata, progress=False)
    assert len(resdf) == 2
    assert resdf.iloc[0].dwelling_matchtype == 'Ambiguous (Raphael)'
    assert resdf.iloc[0].dwelling_numposs == 2

    ## Test 4: No dwelling dates
    mockdata = pd.DataFrame(
        [
            dict(
                event='E1',
                dwelling='D1',
                event_start='1920-01-24',
                event_end='1920-01-29',
                dwelling_start='',
                dwelling_end='',
                dwelling_address='21 Jump St',
                lat=LATLON_SCO[0] - 0.001,
                lon=LATLON_SCO[1] - 0.001,
            ),
            dict(
                event='E1',
                dwelling='D2',
                event_start='1920-01-24',
                event_end='1920-01-29',
                dwelling_start='',
                dwelling_end='',
                dwelling_address='22 Jump St',
                lat=LATLON_SCO[0] - 0.002,
                lon=LATLON_SCO[1] - 0.002,
            ),
        ]
    )

    resdf = prune_when_dwelling_matches(mockdata, progress=False)
    assert len(resdf) == 2
    assert resdf.iloc[0].dwelling_matchtype == 'Ambiguous (Colens)'
    assert resdf.iloc[0].dwelling_numposs == 2

    ## Test 5: Just one
    mockdata = pd.DataFrame(
        [
            dict(
                event='E1',
                dwelling='D1',
                event_start='1920-01-24',
                event_end='1920-01-29',
                dwelling_start='',
                dwelling_end='',
                dwelling_address='21 Jump St',
                lat=LATLON_SCO[0] - 0.001,
                lon=LATLON_SCO[1] - 0.001,
            ),
        ]
    )

    resdf = prune_when_dwelling_matches(mockdata, progress=False)
    assert len(resdf) == 1
    assert resdf.iloc[0].dwelling_matchtype == 'Singular'
    assert resdf.iloc[0].dwelling_numposs == 1

    ## Test 6: Not an event
    mockdata = pd.DataFrame(
        [
            dict(
                event='',
                dwelling='',
                event_start='',
                event_end='',
                dwelling_start='',
                dwelling_end='',
                dwelling_address='21 Jump St',
                lat=LATLON_SCO[0] - 0.001,
                lon=LATLON_SCO[1] - 0.001,
            ),
        ]
    )

    resdf = prune_when_dwelling_matches(mockdata, progress=False)
    assert len(resdf) == 1
    assert resdf.iloc[0].dwelling_matchtype == 'NA'
    assert np.isnan(resdf.iloc[0].dwelling_numposs)
