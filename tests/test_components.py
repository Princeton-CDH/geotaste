import sys,os,tempfile
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# code
from geotaste.imports import *
from pandas.testing import assert_frame_equal, assert_series_equal
from pprint import pprint



def test_BaseComponent():
    bc=BaseComponent(name='test')
    assert bc.name == 'test'
    assert bc.subcomponents == []
    assert bc.cards_with_attr('graph') == []
    assert bc.graph_subcomponents == []
    assert bc.cards_with_attr('children') == []
    assert bc.layout().children == bc.content.children == bc.get_content().children == BLANK

def test_FilterComponent():
    fc=FilterComponent(name='test', figure_factory=FigureFactory)
    assert fc.name == 'test'
    assert hasattr(fc,'store_json')
    assert hasattr(fc,'store_panel')
    assert hasattr(fc,'store_desc')
    assert hasattr(fc,'store')
    
    assert fc.subcomponents == []
    assert fc.cards_with_attr('graph') == []
    assert fc.graph_subcomponents == []
    assert fc.cards_with_attr('children') == []
    assert fc.layout().children == fc.content.children == fc.get_content().children == BLANK

    assert fc.store_json.data == ''
    assert fc.store_panel.data == {}
    assert fc.store_desc.children == BLANK
    assert fc.store.data == {}

    assert len(fc.plot().data[0]['x']) == 0
    assert fc.key == FigureFactory.key

def test_FilterCard():
    fc = FilterCard()
    assert fc.describe_filters({fc.key:['one','two']}) == 'one, two'

def test_FilterSliderCard():
    fc = FilterSliderCard()
    assert fc.describe_filters({fc.key:[1,2]}) == '1 to 2'
    assert fc.describe_filters({fc.key:['a',"b"]}) == 'a to b'

def get_callback_func(flask_app, func_name):
    o = []
    for elname,eld in flask_app.callback_map.items():
        if 'callback' in eld:
            func=eld['callback']
            if func.__name__ == func_name:
                o.append(func.__wrapped__)
    return o
    

def test_graph_selection_updated(dash_duo):
    app = get_app()
    flask_app = app.app
    dash_duo.start_server(flask_app)

    funcs = get_callback_func(flask_app, func_name='graph_selection_updated')
    qual_cols = [col for col in Combined().data if col not in set(CombinedDataset._cols_q)|set(CombinedDataset.cols_q)]
    quant_cols = [col for col in Combined().data if col in set(CombinedDataset._cols_q)|set(CombinedDataset.cols_q)]
    for func in funcs:
        res_qual = func({'points': [{'label': 'A'}, {'label': 'B'}]})
        res_quant = func({'points': [{'label': 1}, {'label': 2}]})
        res_geo = func({'points': [{'location': 1.0}, {'location': 2.0}]})
        assert res_qual and res_quant and res_geo
        key=list(res_qual.keys())[0]
        print(key,key in qual_cols, key in quant_cols)
        if key in qual_cols:
            # assert res_qual == {key:['A','B']}
            assert_series_equal(pd.Series(res_qual), pd.Series({key:['A','B']}))
            assert_series_equal(pd.Series(res_quant), pd.Series({key:['1','2']}))
            assert_series_equal(pd.Series(res_geo), pd.Series({key:['1.0','2.0']}))
        elif key in quant_cols:
            assert_series_equal(pd.Series(res_qual), pd.Series({key:[np.nan,np.nan]}))
            assert_series_equal(pd.Series(res_quant), pd.Series({key:[1,2]}))
            assert_series_equal(pd.Series(res_geo), pd.Series({key:[1.0,2.0]}))