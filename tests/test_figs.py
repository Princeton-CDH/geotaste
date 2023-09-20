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

        # test selections
        ff = FigureFactory(key='key', selected=['Record Key'], dataset_class=DatasetTemp)
        assert len(ff.selection_data.get(ff.key))
        assert len(ff.selected_indices)
        assert len(ff.df_selections)
        assert ff.has_selected() == True
        assert ff.get_selected({'points': [{'label': 'A'}, {'label': 'B'}]}) == {ff.key: ['A','B']}
        assert ff.filter_desc == ''
        assert not ff.filtered

        # test filtering
        ff=FigureFactory(filter_data={'key':'Second Key'}, key='key', dataset_class=DatasetTemp)
        assert ff.filtered
        assert len(ff.filter_data)
        assert 'Second Key' in ff.filter_desc
        assert len(ff.data) < numrows