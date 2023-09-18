from selenium import webdriver
# import chromedriver_binary  # Adds chromedriver binary to path


import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from geotaste.imports import *
from dash.testing.application_runners import import_app



def test_showhide_components(dash_duo):
    # app = import_app('geotaste.app')
    app = get_app()
    dash_duo.start_server(app.app)

    assert dash_duo.find_element('.modal-title').text == WELCOME_HEADER
    dash_duo.multiple_click('#welcome-modal .btn-close', 1)

    assert dash_duo.find_element('#logo_popup').text == SITE_TITLE

    
    panel_clicks = [
        '#button_showhide-Filter_1',
        '#button_showhide-MP-Filter_1',
        '#button_showhide-BP-Filter_1',
        '#button_showhide-Filter_2',
        '#button_showhide-MP-Filter_2',
        '#button_showhide-BP-Filter_2'
    ]
    button_showhide_ids = [
        '#'+x.get_attribute('id')
        for x in dash_duo.find_elements('.button_showhide')
        if '#'+x.get_attribute('id') not in set(panel_clicks)
    ]

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
            

    test_button_showhide_l(panel_clicks)
    test_button_showhide_l(button_showhide_ids, close=True)



# def test_filtering(dash_duo):
#     app = get_app()
#     dash_duo.start_server(app.app)


    ## working idiosyncratically ->

    # click_y_US = .2
    # click_y_FR = .22

    # dash_duo.multiple_click('#welcome-modal .btn-close', 1)
    # dash_duo.multiple_click('#button_showhide-Filter_1', 1)
    # dash_duo.multiple_click('#button_showhide-MP-Filter_1', 1)
    # dash_duo.multiple_click('#button_showhide-MemberNationalityCard-MP-Filter_1', 1)
    # dash_duo.click_at_coord_fractions('#graph-MemberNationalityCard-MP-Filter_1', .7, click_y_US) # click US ?
    # dash_duo.click_at_coord_fractions('#graph-MemberNationalityCard-MP-Filter_1', .7, click_y_US) # click US ?
    # dash_duo.wait_for_contains_text('#store_desc-Filter_1', 'United States')

    # time.sleep(1)

    # # second
    # dash_duo.multiple_click('#button_showhide-Filter_2', 1)
    # dash_duo.multiple_click('#button_showhide-MP-Filter_2', 1)
    # dash_duo.multiple_click('#button_showhide-MemberNationalityCard-MP-Filter_2', 1)
    # dash_duo.click_at_coord_fractions('#graph-MemberNationalityCard-MP-Filter_2', .7, click_y_FR) # click FR ?
    # dash_duo.click_at_coord_fractions('#graph-MemberNationalityCard-MP-Filter_2', .7, click_y_FR) # click FR ?
    # dash_duo.wait_for_contains_text('#store_desc-Filter_2', 'France')