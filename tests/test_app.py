import sys,os,tempfile
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from geotaste.imports import *
from dash.testing.application_runners import import_app
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import requests,bs4

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




def test_suites(dash_duo):
    app = get_app()
    dash_duo.start_server(app.app)
    dash_duo.multiple_click('#welcome-modal .btn-close', 1)
    dash_duo.multiple_click('#tab_table', 1)
    dash_duo.wait_for_contains_text('#tblview','landmarks')

    # open panels
    for idx in [
        '#button_showhide-Filter_1',
        '#button_showhide-Filter_2',
        '#button_showhide-MP-Filter_1',
        '#button_showhide-MP-Filter_2',
        # '#button_showhide-MemberNationalityCard-MP-Filter_1',
        # '#button_showhide-MemberNationalityCard-MP-Filter_2',
    ]:
        dash_duo.multiple_click(idx, 1)
    
    # show test suite buttons
    dash_duo.multiple_click('#test_suite_btn', 1)

    # this btn puts {'member_nationalities':['France]} in L.member_panel.nation_card.store
    dash_duo.multiple_click('#test_suite_btn1', 1)
    dash_duo.wait_for_contains_text('#store_desc-Filter_1', 'France')
    dash_duo.wait_for_contains_text('#tblview','members')
    
    # this btn puts {'member_nationalities':['United States]} in R.member_panel.nation_card.store
    dash_duo.multiple_click('#test_suite_btn2', 1)
    dash_duo.wait_for_contains_text('#store_desc-Filter_2', 'United States')
    dash_duo.wait_for_contains_text('#tblview','comparing')
    
    # clear right by clicking filter clear
    dash_duo.multiple_click('#button_clear-MemberNationalityCard-MP-Filter_2', 1)
    dash_duo.wait_for_text_to_equal('#store_desc-MemberNationalityCard-MP-Filter_2', BLANK)
    dash_duo.wait_for_text_to_equal('#store_desc-Filter_2', BLANK)

    # clear left by clicking top clear
    dash_duo.multiple_click('#button_clear-Filter_1', 1)
    dash_duo.wait_for_text_to_equal('#store_desc-Filter_1', BLANK)
    dash_duo.wait_for_text_to_equal('#store_desc-MemberNationalityCard-MP-Filter_1', BLANK)


    # panel filter
    dash_duo.multiple_click('#button_showhide-MemberNationalityCard-MP-Filter_1', 1)
    dash_duo.wait_for_contains_text('#graph-MemberNationalityCard-MP-Filter_1', '4031')
    dash_duo.multiple_click('#test_suite_btn5', 1)
    time.sleep(10)
    try:
        dash_duo.wait_for_contains_text('#graph-MemberNationalityCard-MP-Filter_1', '4031')
        assert False, 'should not contain class'
    except TimeoutException:
        assert True


def test_query_strings(dash_duo):
    app = get_app()
    dash_duo.start_server(app.app)
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)#, executable_path="/usr/local/bin/chromedriver")

    connected = False
    for host in TEST_HOSTS:
        try:
            driver.get(f'{host}')            
        except Exception as e:
            logger.error(e)
            continue

        connected = True

        logger.debug('Testing no filters')
        time.sleep(10)
        assert driver.find_element_by_id('store_desc-Filter_1').text == BLANK
        assert driver.find_element_by_id('store_desc-Filter_2').text == BLANK

        logger.debug('Testing one filter')
        driver.get(f'{host}?member_gender=Female')
        time.sleep(10)
        el = driver.find_element_by_id('store_desc-Filter_1')
        assert 'Female' in el.text
        driver.get(f'{host}?member_gender2=Male')
        time.sleep(10)
        el = driver.find_element_by_id('store_desc-Filter_2')
        assert 'Male' in el.text


        logger.debug('Testing two filters')
        driver.get(f'{host}?member_gender=Female&member_gender2=Male')
        time.sleep(10)
        el = driver.find_element_by_id('store_desc-Filter_1')
        assert 'Female' in el.text
        el = driver.find_element_by_id('store_desc-Filter_2')
        assert 'Male' in el.text


        logger.debug('Testing tab')
        driver.get(f'{host}?tab=table')
        time.sleep(10)
        el = driver.find_element_by_id('tblview')
        assert el.is_displayed()
        driver.get(f'{host}?tab=map')
        time.sleep(10)
        el = driver.find_element_by_id('tblview')
        assert not el.is_displayed()


        logger.debug('Testing tab2')
        driver.get(f'{host}?tab=table&tab2=book&member_gender=Female&member_gender2=Male')
        time.sleep(10)
        el = driver.find_element_by_id('maintbl-container')
        assert 'Fiction' in el.text
        assert 'Poetry' in el.text

        logger.debug('Testing lat/long/zoom query params')
        driver.get(f'{host}?lat=48.85697&lon=2.32748&zoom=16.23372')
        time.sleep(10)
        el = driver.find_element_by_id('mainmap')
        assert el.is_displayed()

        driver.get(f'{host}?tab=map')
        time.sleep(10)
        assert 'lat=' not in driver.current_url

        driver.find_element_by_id('test_suite_btn').click()
        time.sleep(10)

        driver.find_element_by_id('test_suite_btn4').click()
        time.sleep(10)

        assert 'lat=' in driver.current_url
        assert 'lon=' in driver.current_url
        assert 'zoom=' in driver.current_url

        # close
        driver.close()

        assert connected, "Never connected"