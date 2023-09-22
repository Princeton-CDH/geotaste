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
    fc=FilterComponent(name='test')
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