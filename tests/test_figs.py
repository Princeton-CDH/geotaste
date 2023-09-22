import sys,os,tempfile
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# code
from geotaste.imports import *
from pandas.testing import assert_frame_equal
from pprint import pprint

all_figs = [v for k,v in globals().items() if k.endswith('Figure')]


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

def test_all_figs():
    fdata={'member_gender':['Male','Female']}
    for fig_class in all_figs:
        ff=fig_class(fdata)
        assert ff.filter_data == fdata
        assert len(ff.data) < len(ff.data_orig)
        if ff.drop_duplicates:
            assert len(ff.data.drop_duplicates(ff.drop_duplicates)) == len(ff.data)
        if ff.key:
            fig=ff.plot()
            figdat=fig.data[0]
            assert len(figdat['x'])
            assert len(figdat['y'])


def test_LandmarksFigureFactory():
    ff=LandmarksFigureFactory()
    assert_frame_equal(ff.data, LandmarksDataset().data)
    fig=ff.plot_map()
    figdat=fig.data[0]
    laydat=json.loads(fig.layout.to_json())
    assert len(figdat['lat'])
    assert len(figdat['lon'])
    assert len(figdat['text'])
    assert laydat.get('mapbox',{}).get('layers',{})



def assert_frame_not_equal(*args, **kwargs):
    try:
        assert_frame_equal(*args, **kwargs)
    except AssertionError:
        # frames are not equal
        pass
    else:
        # frames are equal
        raise AssertionError



def test_CombinedFigureFactory():
    ff=CombinedFigureFactory()
    assert_frame_equal(ff.data, ff.data_orig)
    assert_frame_equal(ff.data_orig, Combined().data)

    assert_frame_equal(ff.df_dwellings.reset_index().drop_duplicates('dwelling'), ff.df_dwellings.reset_index())
    assert_frame_equal(ff.df_members.reset_index().drop_duplicates('member'), ff.df_members.reset_index())


    assert not ff.book_filters_exist
    assert not ff.filtered

    assert {d['id'] for d in ff.table().columns} == set(ff.cols_table_members)

    fd={'book_genre':['Fiction']}
    ff=CombinedFigureFactory(fd)
    assert ff.book_filters_exist
    assert ff.filtered
    assert ff.filter_data==fd
    assert len(ff.data)<len(ff.data_orig)
    assert_frame_equal(ff.data_orig, Combined().data)
    assert_frame_not_equal(ff.data, ff.data_orig)
    assert set(flatten_series(ff.data.book_genre)) == {'Fiction'}
    fig=ff.plot_map()
    figdat=fig.data[0]
    laydat=json.loads(fig.layout.to_json())
    assert len(figdat['lat'])
    assert len(figdat['lon'])
    assert len(figdat['text'])
    assert not laydat.get('mapbox',{}).get('layers',{}) # only landmarks

def test_ComparisonFigureFactory():
    # test case 1: empty
    ff=ComparisonFigureFactory()
    assert isinstance(ff.L, CombinedFigureFactory)
    assert isinstance(ff.R, CombinedFigureFactory)
    assert not ff.L.filtered
    assert not ff.R.filtered
    odf=ff.compare()
    assert set(odf.odds_ratio.unique()) == {1.0}
    assert set(odf.fisher_exact_p.unique()) == {1.0}
    desc_L,desc_R=ff.describe_comparison(odf)
    assert not desc_L
    assert not desc_R
    fig=ff.plot_oddsratio_map()
    figdat=json.loads(fig.data[0].to_json())
    laydat=json.loads(fig.layout.to_json())
    assert len(figdat['geojson']['features'])
    assert not laydat.get('mapbox',{}).get('layers',{}) # only landmarks



    # test case 2: filtered
    ff=ComparisonFigureFactory(
        {'member_nationalities':['France']},
        {'member_nationalities':['United States']}
    )
    assert len(ff.L.data)
    assert len(ff.R.data)
    assert isinstance(ff.L, CombinedFigureFactory)
    assert isinstance(ff.R, CombinedFigureFactory)
    assert ff.L.filtered
    assert ff.R.filtered
    odf=ff.compare()
    assert set(odf.odds_ratio.unique()) != {1.0}
    assert set(odf.fisher_exact_p.unique()) != {1.0}
    desc_L,desc_R=ff.describe_comparison(odf)
    assert desc_L
    assert desc_R
    fig=ff.plot_oddsratio_map()
    figdat=json.loads(fig.data[0].to_json())
    laydat=json.loads(fig.layout.to_json())
    assert len(figdat['geojson']['features'])
    assert not laydat.get('mapbox',{}).get('layers',{}) # only landmarks


def test_get_dash_table():
    df=pd.DataFrame([
        {'a':random.random(), 'b':random.random(), 'i':i}
        for i in range(100)
    ])
    dtbl=get_dash_table(df)
    assert len(dtbl.columns) == 3
    dtbl=get_dash_table(df, cols=['a','i'])
    assert len(dtbl.columns) == 2
    assert len(dtbl.data) == 100

def test_get_empty_fig():
    fig=get_empty_fig()
    assert not fig.data
    
def test_plot_cache():
    for fc in all_figs:
        fig1 = plot_cache(fc, serialize([{},[],{}]))
        fig2 = plot_cache(fc)
        fig3 = fc().plot()
        fig4 = plot_cache(fc,serialize([{'member_gender':['Female']},[],{}]))
        fig5 = fc({'member_gender':['Female']}).plot()

        fdat1=json.loads(from_json_gz_str(fig1).data[0].to_json())
        fdat2=json.loads(from_json_gz_str(fig2).data[0].to_json())
        fdat3=json.loads(fig3.data[0].to_json())
        fdat4=json.loads(from_json_gz_str(fig4).data[0].to_json())
        fdat5=json.loads(fig5.data[0].to_json())
        for fdat in [fdat1,fdat2,fdat3,fdat4,fdat5]:
            if 'text' in fdat:
                del fdat['text']

        assert type(fig1) is str
        assert type(fig1) is str
        assert fdat1 == fdat2
        assert fdat2 == fdat3

        assert set(fdat4['x']) == set(fdat5['x'])
        assert set(fdat4['y']) == set(fdat5['y'])


def test_get_ff_for_num_filters():
    ff=get_ff_for_num_filters()
    assert type(ff) is LandmarksFigureFactory

    ff=get_ff_for_num_filters({'a':[1]})
    assert type(ff) is CombinedFigureFactory
    ff=get_ff_for_num_filters({}, {'a':[1]})
    assert type(ff) is CombinedFigureFactory
    ff=get_ff_for_num_filters({'b':[2]}, {'a':[1]})
    assert type(ff) is ComparisonFigureFactory


def test_get_cached_fig_or_table():
    def get(fdL={},fdR={},tab='map',analysis_tab=''):
        return from_json_gz_str(
            get_cached_fig_or_table(
                serialize(
                    [fdL,fdR,tab,analysis_tab]
                )
            )
        )
    
    mapfig1=get()
    mapfig2=get({'book_genre':['Fiction']})
    mapfig3=get({}, {'book_genre':['Fiction']})
    mapfig4=get({'book_genre':['Poetry']}, {'book_genre':['Fiction']})
    
    assert mapfig1.data[0].name.startswith('Landmark')
    assert mapfig2.data[0].name.startswith('Member')
    assert mapfig3.data[0].name.startswith('Member')
    assert mapfig4.data[0].name.startswith('Member')

    assert mapfig2.data[0]['marker']['color'] == LEFT_COLOR
    assert mapfig3.data[0]['marker']['color'] == RIGHT_COLOR
    
    assert len(mapfig4.data)==2
    assert mapfig4.data[0]['marker']['color'] == LEFT_COLOR
    assert mapfig4.data[1]['marker']['color'] == LEFT_COLOR

    tblfig1=get(tab='table')
    tblfig2=get({'book_genre':['Fiction']}, tab='table')
    tblfig3=get({}, {'book_genre':['Fiction']}, tab='table')
    tblfig4=get({'book_genre':['Poetry']}, {'book_genre':['Fiction']}, tab='table')

    tbldat1=tblfig1.get('props',{}).get('data',[])
    tbldat2=tblfig2.get('props',{}).get('data',[])
    tbldat3=tblfig3.get('props',{}).get('data',[])    
    assert 'landmark' in tbldat1[0], 'landmark dataset in first case'
    assert 'member_name' in tbldat2[0], 'members dataset in 2nd case'
    assert 'member_name' in tbldat3[0], 'members dataset in 3rd case'
    assert 'children' in tblfig4['props'], 'Comparison output not a table but a Container'


def test_from_json_gz_str():
    obj = go.Figure()
    assert from_json_gz_str(to_json_gz_str(obj)) == obj
    assert type(to_json_gz_str(obj)) == str

def test_update_fig_mapbox_background():
    fig=go.Figure()
    laydat=json.loads(fig.layout.to_json())
    assert not laydat.get('mapbox',{}).get('layers',{})

    update_fig_mapbox_background(fig)
    laydat=json.loads(fig.layout.to_json())
    assert laydat.get('mapbox',{}).get('layers',{})


def test_get_selected_records_from_figure_selected_data():
    #@TODO
    pass