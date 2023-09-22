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
                o.append((elname,func.__wrapped__))
    return o
    

def test_graph_selection_updated(dash_duo):
    app = get_app()
    flask_app = app.app
    dash_duo.start_server(flask_app)
    funcs = get_callback_func(flask_app, func_name='graph_selection_updated')
    for elname,func in funcs:
        elx='#'+elname.split('.')[0]
        elxid=elx.split('-',1)[-1]
        cardname=elxid.split('-')[0]
        card=globals()[cardname]
        ff=card().ff()
        if not ff.quant:
            val = random.choice(list(ff.get_unique_vals()))
            res = func({'points': [{'label': val}]})
            correct = {ff.key:[val]}
            assert_series_equal(pd.Series(res), pd.Series(correct))


## Can't trigger callback? -->

# def test_panel_data_updated(dash_duo):
#     app = get_app()
#     flask_app = app.app
#     dash_duo.start_server(flask_app)
#     with app.ctx.callback_context:

#         print(globals().keys())
#         all_cards = {x:globals()[x]() for x in globals() if 'Card' in x}
#         funcs = get_callback_func(flask_app, func_name='panel_data_updated')
#         print(all_cards.keys())
#         for elname,func in funcs:
#             cardname=elname.split('-')[1]
#             print(cardname,'?')
#             if not 'Card' in cardname or not cardname in all_cards: continue
#             card=all_cards[cardname]
#             ff=card.ff()
#             val = random.choice(list(ff.get_unique_vals()))
#             filterd = {ff.key: [val]}

#             other_card = random.choice([c for cname,c in all_cards.items() if c is not None and cname != cardname])
#             other_ff = other_card.ff()
#             other_val = random.choice(list(other_ff.get_unique_vals()))
#             other_filterd = {other_ff.key : [other_val]}
            
#             res = func(
#                 panel_filter_data=other_filterd, 
#                 my_filter_data=filterd, 
#                 _clicked_open_1=1,
#                 _clicked_open_2=1, 
#                 current_sels={}
#             )
#             print(res)