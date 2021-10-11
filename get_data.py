from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from pprint import pprint
import os
import time
import json


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('window-size=1920,1080')
driver = webdriver.Chrome(options=chrome_options)
wait_for_condition = WebDriverWait(driver, 5)


selectors = {
    'usa_box': 'div[id="wd-Facet-locationCountry"] div[data-automation-id="checkboxPanel"]:nth-of-type(1)',
    'entry': ('li[data-automation-id="compositeContainer"]'
              '[id^="wd-CompositeWidget-templatedListItem"]'
              ' div[data-automation-id="compositeHeader"]'),
    'first_entry': 'div.gwt-Label[role="link"]:nth-of-type(1)',
    'nth_entry': ('li[data-automation-id="compositeContainer"]'
                  '[id^="wd-CompositeWidget-templatedListItem"]'
                  ':nth-of-type({entry_num}) div[data-automation-id="compositeHeader"]'),
    'content_block': '[data-automation-id="pageMainContent"]',
    'geo_loc': '#labeledImage\.LOCATION div.gwt-Label',
    'job_id': '[data-metadata-id="labeledImage.JOB_REQ"] div.gwt-Label[id^="promptOption-gwt-uid"]',
    'job_title': '#richTextArea\.jobPosting\.title-input--uid4-input > div.GWTCKEditor-Disabled > h1',
    'job_description': 'div[data-metadata-id="richTextArea.jobPosting.jobDescription"]',
    'search_results': '[id="wd-FacetedSearchResultList-PaginationText-facetSearchResultList.newFacetSearch.Report_Entry"]'
}


def search_latency(web_driver):
    def outer_wrapper(func):
        def inner_wrapper(*args, **kwargs):
            return web_driver.until(func(*args, **kwargs))
        return inner_wrapper
    return outer_wrapper


@search_latency(wait_for_condition)
def locate_presence(selector, multiple=False):
    """
    Function serving as an alias for locating presence of element using CSS selector.
    :param selector:
    :param multiple:
    :return:
    """
    if multiple:
        return EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
    return EC.presence_of_element_located((By.CSS_SELECTOR, selector))


def go_to_nth_entry(entry_num):
    try:
        next_entry_link = locate_presence(selectors['nth_entry'].format(entry_num=entry_num))
    except TimeoutException as TE:
        print(TE)
        return False
    new_tab_chains = ActionChains(driver)
    new_tab_chains.key_down(Keys.CONTROL).click(next_entry_link).key_up(Keys.CONTROL).perform()
    driver.switch_to.window(driver.window_handles[-1])
    return True


def get_job_info():
    temp_dict = {'locations': ''}
    locations = locate_presence(selectors['geo_loc'], True)
    for location in locations:
        temp_dict['locations'] += (location.text + '; ')
    temp_dict['locations'] = temp_dict['locations'][:-2]
    # print(temp_dict['locations'])
    temp_dict['job_url'] = driver.current_url
    temp_dict['job_id'] = locate_presence(selectors['job_id']).text
    temp_dict['job_title'] = locate_presence(selectors['job_title']).text
    temp_dict['job_description'] = locate_presence(selectors['job_description']).text
    return temp_dict


def main():
    driver.get('https://abglobal.wd1.myworkdayjobs.com/alliancebernsteincareers')
    results = []
    usa_box = locate_presence(selectors['usa_box'])
    time.sleep(2)
    pre_box_entry = driver.find_element_by_css_selector(selectors['first_entry'])
    usa_box.click()
    wait_for_detach = wait_for_condition.until(EC.staleness_of(pre_box_entry))
    post_box_entry = locate_presence(selectors['first_entry'])
    search_results = driver.find_element_by_css_selector(selectors['search_results']).text
    first_batch_page = 0
    with open('results.json', 'r+', encoding='utf-8') as file:
        lines_count = len(file.readlines())
        print(f'{lines_count} links were already preprocessed. Continuing from {lines_count+1}')
        next_entry_num = lines_count + 1

    with open('results.json', 'w', encoding='utf-8') as new_res:
        new_res.write('[')
    link_counter = 0

    while True:
        if go_to_nth_entry(next_entry_num):
            wait_for_content = locate_presence(selectors['content_block'])
            results.append(get_job_info())
            pprint(results[-1])
            with open('results.json', 'a', encoding='utf-8') as file:
                json.dump(results[-1], file)
                file.write(',')
                file.write('\n')
            time.sleep(1.5)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            print(f'{next_entry_num}/{search_results} (results number may have changed)')
            next_entry_num += 1
            time.sleep(1.5)
        else:
            last_entry_num = len(driver.find_elements_by_css_selector(selectors['entry']))
            if last_entry_num >= first_batch_page + 50:
                first_batch_page = last_entry_num
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            else:
                print('Looks like we ran out of entries')
                break
            # print(len(results))

    with open('results.json', 'r+') as file:
        file.seek(0, os.SEEK_END)
        file.seek(file.tell()-2, os.SEEK_SET)
        file.write(']')
    driver.quit()


if __name__ == '__main__':
    main()



