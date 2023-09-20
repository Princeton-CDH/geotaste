import sys,os,tempfile
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# code
from geotaste.imports import *
from pandas.testing import assert_frame_equal

def test_FigureFactory():
    ## get dataset
    with tempfile.TemporaryDirectory() as tdir:
        numrows = 100
        df = pd.DataFrame(
            {'a':random.random(), 'b':random.random(), 'c':random.random(), 'key':'Record Key' if random.random()>.5 else 'Second Key'}
            for n in range(numrows)
        )
        ofn=os.path.join(tdir,'data.csv')
        df.to_csv(ofn, index=False)
    
        class DatasetTemp(Dataset):
            path = ofn

        ff = FigureFactory(
            key='key',
            dataset_class=DatasetTemp
        )
        print(ff.data)

        # Test instance creation and default property values
        assert ff.key == 'key'
        assert isinstance(ff.dataset_class, type(DatasetTemp))
        assert len(ff.data) == numrows
        assert_frame_equal(ff.data, df)
        assert isinstance(ff.data_orig, pd.DataFrame)
        assert isinstance(ff.data, pd.DataFrame)
        
        # Test the has_selected method
        assert not len(ff.selection_data.get(ff.key))
        assert ff.has_selected() == False
        assert ff.get_selected() == {ff.key: []} or ff.get_selected() == {ff.key: {}}
        assert not ff.plot().data[0]['selectedpoints']

        # test selections
        ff = FigureFactory(key='key', selected=['Record Key'], dataset_class=DatasetTemp)
        assert len(ff.selection_data.get(ff.key))
        assert len(ff.selected_indices)
        assert len(ff.df_selections)
        assert ff.has_selected() == True
        assert ff.get_selected({'points': [{'label': 'A'}, {'label': 'B'}]}) == {ff.key: ['A','B']}
        assert ff.filter_desc == ''
        assert not ff.filtered
        assert ff.plot().data[0]['selectedpoints']

        print(ff.plot().data)

        # test filtering
        ff=FigureFactory(filter_data={'key':'Second Key'}, key='key', dataset_class=DatasetTemp)
        assert ff.filtered
        assert len(ff.filter_data)
        assert 'Second Key' in ff.filter_desc
        assert len(ff.data) < numrows
        assert all(np.isnan(x) for x in ff.get_series(quant=True))
        assert set(ff.get_series(quant=False, df=ff.data_orig).unique()) == {'Record Key', 'Second Key'}
        assert set(ff.series_orig.unique()) == {'Record Key', 'Second Key'}
        assert set(ff.get_series(quant=False, df=ff.data).unique()) == {'Second Key'}
        assert set(ff.get_series(quant=False).unique()) == {'Second Key'}
        assert set(ff.series.unique()) == {'Second Key'}

        # test other
        ff = FigureFactory(key='key', dataset_class=DatasetTemp)
        assert not any(np.isnan(x) for x in ff.df_counts['count'])
        fig=ff.plot()
        assert len(fig.data[0]['x'])
        assert len(fig.data[0]['y'])

        tbl=ff.table(cols=['a','b','c','key'])
        assert isinstance(tbl, dash_table.DataTable)
        assert len(tbl.data)
        assert len(tbl.columns)