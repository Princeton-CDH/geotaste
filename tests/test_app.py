from selenium import webdriver
# import chromedriver_binary  # Adds chromedriver binary to path


import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from geotaste.imports import *
from dash.testing.application_runners import import_app
# 


def test_showhide_components(dash_duo):
    # app = import_app('geotaste.app')
    app = get_app()
    dash_duo.start_server(app.app)

    assert dash_duo.find_element('.modal-title').text == WELCOME_HEADER
    dash_duo.multiple_click('#welcome-modal .btn-close', 1)

    assert dash_duo.find_element('#logo_popup').text == SITE_TITLE

    def test_button_showhide_l(button_showhide_ids, close=False):    
        for btn_id in button_showhide_ids:
            body_id='#body-'+btn_id.split('-',1)[-1]
            logger.debug(body_id)
            assert dash_duo.wait_for_style_to_equal(body_id,'display','none')
            logger.debug(btn_id)
            dash_duo.multiple_click(btn_id, 1)
            assert dash_duo.wait_for_style_to_equal(body_id,'display','block')

            if close:
                dash_duo.multiple_click(btn_id, 1)
                assert dash_duo.wait_for_style_to_equal(body_id,'display','none')

    
    button_showhide_ids = [
        '#'+x.get_attribute('id')
        for x in dash_duo.find_elements('.button_showhide')
    ]

    member_cards1 = [x for x in button_showhide_ids if '-MP-' in x and 'Card' in x and 'Filter_1' in x]
    member_cards2 = [x for x in button_showhide_ids if '-MP-' in x and 'Card' in x and 'Filter_2' in x]
    book_cards1 = [x for x in button_showhide_ids if '-BP-' in x and 'Card' in x and 'Filter_1' in x]
    book_cards2 = [x for x in button_showhide_ids if '-BP-' in x and 'Card' in x and 'Filter_2' in x]

    top_panel_ids=[
        '#button_showhide-Filter_1',
        '#button_showhide-Filter_2',
    ]

    mpbp_ids=[
        '#button_showhide-MP-Filter_1',
        '#button_showhide-BP-Filter_1',
        '#button_showhide-MP-Filter_2',
        '#button_showhide-BP-Filter_2'
    ]

    test_button_showhide_l(top_panel_ids, close=False)
    test_button_showhide_l(mpbp_ids, close=True)

    ## member cards
    dash_duo.multiple_click('#button_showhide-MP-Filter_1', 1)
    test_button_showhide_l(member_cards1, close=True)
    dash_duo.multiple_click('#button_showhide-MP-Filter_1', 1)

    dash_duo.multiple_click('#button_showhide-MP-Filter_2', 1)
    test_button_showhide_l(member_cards2, close=True)
    dash_duo.multiple_click('#button_showhide-MP-Filter_2', 1)

    ## book cards
    dash_duo.multiple_click('#button_showhide-BP-Filter_1', 1)
    test_button_showhide_l(book_cards1, close=True)
    dash_duo.multiple_click('#button_showhide-BP-Filter_1', 1)

    dash_duo.multiple_click('#button_showhide-BP-Filter_2', 1)
    test_button_showhide_l(book_cards2, close=True)
    dash_duo.multiple_click('#button_showhide-BP-Filter_2', 1)




def get_ids(els):
    return [f'#{el.get_attribute("id")}' for el in els]


## doesnt work on github actions?

# def test_filtering(dash_duo):
#     app = get_app()
#     dash_duo.start_server(app.app)

#     click_y_US = .22
#     click_y_FR = .24

#     dash_duo.multiple_click('#welcome-modal .btn-close', 1)
#     dash_duo.multiple_click('#button_showhide-Filter_1', 1)
#     dash_duo.multiple_click('#button_showhide-MP-Filter_1', 1)
#     dash_duo.multiple_click('#button_showhide-MemberNationalityCard-MP-Filter_1', 1)
#     time.sleep(1)
#     dash_duo.click_at_coord_fractions('#graph-MemberNationalityCard-MP-Filter_1', .7, click_y_US) # click US ?
#     dash_duo.click_at_coord_fractions('#graph-MemberNationalityCard-MP-Filter_1', .7, click_y_US) # click US ?
#     dash_duo.wait_for_contains_text('#store_desc-Filter_1', 'United States')

#     time.sleep(1)

#     # second
#     dash_duo.multiple_click('#button_showhide-Filter_2', 1)
#     dash_duo.multiple_click('#button_showhide-MP-Filter_2', 1)
#     dash_duo.multiple_click('#button_showhide-MemberNationalityCard-MP-Filter_2', 1)
#     time.sleep(1)
#     dash_duo.click_at_coord_fractions('#graph-MemberNationalityCard-MP-Filter_2', .7, click_y_FR)
#     dash_duo.click_at_coord_fractions('#graph-MemberNationalityCard-MP-Filter_2', .7, click_y_FR)
#     dash_duo.wait_for_contains_text('#store_desc-Filter_2', 'France')

