from config.settings.base import (DEBUG,
                                  MAIN_SITE,
                                  CHROME_DRIVER_PATH)
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


def setup_driver():
    # Make sure you have chrome driver in path
    chrome_options = Options()
    # If not in debug, dont open browser ui
    # if not DEBUG:
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=chrome_options)
    driver.get(MAIN_SITE)
    return driver


def get_essay_title_and_contents(driver):
    if DEBUG:
        # if in debug mode, read from predownloaded list rather download all which is slow
        with open('essays.array', 'r') as r:
            essay_titles_bodies = eval(r.read())
    else:
        # This xpath finds all essay links from articles page
        elements = driver.find_elements_by_xpath("//td[@width=435]/font/a")
        first_link = elements[0]

        essay_titles_bodies = []

        # Get essay titles and contents

        for i in range(len(elements)):
        # Looping backwards for debugging
        #for i in range(len(elements) - 1, len(elements) - 20, -1):
            # Need to get elements every time the page is loaded
            # so the hack below is neccessary
            if i == 0:
                current_link = first_link
            else:
                current_link = elements[i]
            essay_title = current_link.text
            current_link.click()

            # This hack is neccessarry due to inconsistent site strucutre
            if re.search(r'Chapter [12] of Ansi Common Lisp', essay_title):
                # These 2 essay bodies are in pre tag
                essay_body = driver.find_element_by_xpath('//pre').text
            elif essay_title == 'Lisp for Web-Based Applications':
                essay_body = driver.find_element_by_xpath('//p').text
            else:
                # There are essays where the content is placed in multiple
                # font tags so need the catch 'em all
                body_elements = driver.find_elements_by_xpath("//font[@size=2][@face='verdana']")
                essay_body = '\n'.join([x.text for x in body_elements])
                #essay_body = driver.find_element_by_xpath("//tr[@valign='top']").text

            essay_titles_bodies.append((essay_title, essay_body))
            driver.back()

            elements = driver.find_elements_by_xpath("//td[@width=435]/font/a")
    return essay_titles_bodies
