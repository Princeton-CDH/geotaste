import subprocess,logging
from multiprocessing import Process, Queue
import sys,os,tempfile
sys.path.insert(0,os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from geotaste.imports import *
from dash.testing.application_runners import import_app
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import requests,bs4,flask

NAPTIME = int(os.environ.get('NAPTIME', 5))
def _nap(naptime=NAPTIME): time.sleep(naptime)



def test_showhide_components(dash_duo):
    # app = import_app('geotaste.app')
    app = get_app()
    dash_duo.start_server(app.app)

    # modal open
    assert dash_duo.find_element('#welcome-modal .modal-title').text == WELCOME_HEADER
    # close modal
    dash_duo.multiple_click('#welcome-modal .btn-close', 1)
    _nap()
    # modal ought to be closed
    try:
        dash_duo.find_element('#welcome-modal .modal-title')
        assert False, 'should be gone'
    except Exception:
        assert True, 'correctly not found'

    # open modal another way
    dash_duo.multiple_click('#welcome_modal_info_btn', 1)
    _nap(5 if NAPTIME < 5 else NAPTIME)
    # modal ought to be open
    assert dash_duo.find_element('#welcome-modal .modal-title').text == WELCOME_HEADER
    # close modal
    dash_duo.multiple_click('#welcome-modal .btn-close', 1)
    _nap()
    # modal ought to be closed
    try:
        dash_duo.find_element('#welcome-modal .modal-title')
        assert False, 'should be gone'
    except Exception:
        assert True, 'correctly not found'





    assert dash_duo.find_element('#donotcite').text == DONOTCITE
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




def test_suites(dash_duo, done=True):
    app = get_app()
    dash_duo.start_server(app.app)
    dash_duo.multiple_click('#welcome-modal .btn-close', 1)
    _nap()
    dash_duo.multiple_click('#tab_table', 1)
    _nap()
    dash_duo.wait_for_contains_text('#tblview','landmarks')

    # open panels
    for idx in [
        '#button_showhide-Filter_1',
        '#button_showhide-Filter_2',
        '#button_showhide-MP-Filter_1',
        '#button_showhide-MP-Filter_2',
    ]:
        dash_duo.multiple_click(idx, 1)
        _nap()
    
    # show test suite buttons
    dash_duo.multiple_click('#test_suite_btn', 1)
    _nap()

    if done:

        # this btn puts {'member_nationalities':['France]} in L.member_panel.nation_card.store
        dash_duo.multiple_click('#test_suite_btn1', 1)
        _nap()
        dash_duo.wait_for_contains_text('#store_desc-Filter_1', 'France')
        dash_duo.wait_for_contains_text('#tblview','members')
        
        # this btn puts {'member_nationalities':['United States]} in R.member_panel.nation_card.store
        dash_duo.multiple_click('#test_suite_btn2', 1)
        _nap()
        dash_duo.wait_for_contains_text('#store_desc-Filter_2', 'United States')
        dash_duo.wait_for_contains_text('#tblview','comparing')
        
        # clear right by clicking filter clear
        dash_duo.multiple_click('#button_clear-MemberNationalityCard-MP-Filter_2', 1)
        _nap()
        dash_duo.wait_for_text_to_equal('#store_desc-MemberNationalityCard-MP-Filter_2', BLANK)
        dash_duo.wait_for_text_to_equal('#store_desc-Filter_2', BLANK)

        # clear left by clicking top clear
        dash_duo.multiple_click('#button_clear-Filter_1', 1)
        _nap()
        dash_duo.wait_for_text_to_equal('#store_desc-Filter_1', BLANK)
        dash_duo.wait_for_text_to_equal('#store_desc-MemberNationalityCard-MP-Filter_1', BLANK)

        # panel filter
        dash_duo.multiple_click('#button_showhide-MemberNationalityCard-MP-Filter_1', 1)
        _nap()
        dash_duo.wait_for_contains_text('#graph-MemberNationalityCard-MP-Filter_1', '4031')
        dash_duo.multiple_click('#test_suite_btn5', 1)
        _nap()
        try:
            dash_duo.wait_for_contains_text('#graph-MemberNationalityCard-MP-Filter_1', '4031')
            assert False, 'should not contain class'
        except TimeoutException:
            assert True
        
        # clear left by clicking top clear
        dash_duo.multiple_click('#button_clear-Filter_1', 1)
        _nap()

        # panel filter
        dash_duo.multiple_click('#button_showhide-MemberNationalityCard-MP-Filter_1', 1)
        dash_duo.multiple_click('#button_showhide-MembershipYearCard-MP-Filter_1', 1)
        _nap()
        dash_duo.wait_for_contains_text('#input_start-MembershipYearCard-MP-Filter_1', '1919')
        dash_duo.multiple_click('#test_suite_btn6', 1)
        _nap()
        dash_duo.wait_for_contains_text('#input_start-MembershipYearCard-MP-Filter_1', '1932')
        dash_duo.wait_for_contains_text('#input_end-MembershipYearCard-MP-Filter_1', '1939')

        # dash_duo.multiple_click('#button_showhide-MembershipYearCard-MP-Filter_1', 1)
        input1 = dash_duo.find_element('#input_start-MembershipYearCard-MP-Filter_1')
        input2 = dash_duo.find_element('#input_end-MembershipYearCard-MP-Filter_1')
        input1.send_keys(Keys.BACKSPACE,Keys.BACKSPACE,Keys.BACKSPACE,Keys.BACKSPACE)
        input1.send_keys('1920')

        input2.send_keys(Keys.BACKSPACE,Keys.BACKSPACE,Keys.BACKSPACE,Keys.BACKSPACE)
        input2.send_keys('1930')
        _nap()
        dash_duo.multiple_click('#input_btn-MembershipYearCard-MP-Filter_1', 1)
        _nap()
        dash_duo.wait_for_contains_text('#input_start-MembershipYearCard-MP-Filter_1', '1920')
        dash_duo.wait_for_contains_text('#input_end-MembershipYearCard-MP-Filter_1', '1930')
        _nap()
        dash_duo.multiple_click('#button_clear-MembershipYearCard-MP-Filter_1', 1)
        _nap()
        dash_duo.wait_for_text_to_equal('#store_desc-MembershipYearCard-MP-Filter_1', BLANK)
        dash_duo.wait_for_text_to_equal('#store_desc-Filter_1', BLANK)





    dash_duo.multiple_click('#button_showhide-MemberNameCard-MP-Filter_1', 1)
    _nap()
    input = dash_duo.find_element('#input-MemberNameCard-MP-Filter_1 input')
    _nap()
    bad='Ryan Heuser'
    input.send_keys(bad)
    _nap()
    # No options to be found with `x` in them, should show the empty message.
    dash_duo.wait_for_text_to_equal(".Select-noresults", "No results found")

    input.send_keys(*[Keys.BACKSPACE for x in bad])
    input.send_keys('James Joyce')
    input.send_keys(Keys.ENTER)
    dash_duo.wait_for_text_to_equal("#store_desc-MemberNameCard-MP-Filter_1", "James Joyce")
    dash_duo.multiple_click('#button_clear-MemberNameCard-MP-Filter_1', 1)
    _nap()
    dash_duo.wait_for_text_to_equal('#store_desc-MemberNameCard-MP-Filter_1', BLANK)
    dash_duo.wait_for_text_to_equal('#store_desc-Filter_1', BLANK)
    




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
        _nap()
        assert driver.find_element_by_id('store_desc-Filter_1').text == BLANK
        assert driver.find_element_by_id('store_desc-Filter_2').text == BLANK

        logger.debug('Testing one filter')
        driver.get(f'{host}?member_gender=Female')
        _nap()
        el = driver.find_element_by_id('store_desc-Filter_1')
        assert 'Female' in el.text
        driver.get(f'{host}?member_gender2=Male')
        _nap()
        el = driver.find_element_by_id('store_desc-Filter_2')
        assert 'Male' in el.text


        logger.debug('Testing two filters')
        driver.get(f'{host}?member_gender=Female&member_gender2=Male')
        _nap()
        el = driver.find_element_by_id('store_desc-Filter_1')
        assert 'Female' in el.text
        el = driver.find_element_by_id('store_desc-Filter_2')
        assert 'Male' in el.text


        logger.debug('Testing tab')
        driver.get(f'{host}?tab=table')
        _nap()
        el = driver.find_element_by_id('tblview')
        assert el.is_displayed()
        driver.get(f'{host}?tab=map')
        _nap()
        el = driver.find_element_by_id('tblview')
        assert not el.is_displayed()


        logger.debug('Testing tab2')
        driver.get(f'{host}?tab=table&tab2=book&member_gender=Female&member_gender2=Male')
        _nap()
        el = driver.find_element_by_id('maintbl-container')
        assert 'Fiction' in el.text
        assert 'Poetry' in el.text

        logger.debug('Testing lat/long/zoom query params')
        driver.get(f'{host}?lat=48.85697&lon=2.32748&zoom=16.23372')
        _nap()
        el = driver.find_element_by_id('mainmap')
        assert el.is_displayed()

        driver.get(f'{host}?tab=map')
        _nap()
        assert 'lat=' not in driver.current_url

        driver.find_element_by_id('test_suite_btn').click()
        _nap()

        driver.find_element_by_id('test_suite_btn4').click()
        _nap()

        assert 'lat=' in driver.current_url
        assert 'lon=' in driver.current_url
        assert 'zoom=' in driver.current_url

        # close
        driver.close()

        assert connected, "Never connected"

def test_get_server():
    server=get_server()
    assert isinstance(server, flask.app.Flask)

    # needs testing in separate thread when not a dry run?
    runner=run(port=1991, dry_run=True)
    assert isinstance(runner, flask.app.Flask)
    
    app=get_app()
    assert isinstance(app, DashApp)
    assert isinstance(app.app, Dash)
    assert isinstance(app.app.server, flask.app.Flask)

def _apprun(q): 
    q.put(run(port=1992))


def test_run():
    try:
        queue = Queue()
        try:
            from pytest_cov.embed import cleanup_on_sigterm
        except ImportError:
            pass
        else:
            cleanup_on_sigterm()

        p = Process(target=_apprun, args=(queue,))
        try:
            p.start()
            time.sleep(10)
        finally:
            p.terminate()
            time.sleep(5)
            p.join()    
            assert True, 'server running succeeded'
    except Exception:
        assert False, 'server running failed'