import os
import logging
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class scraper() :

    # setup login credential and department needed
    def __init__(self, username, password, departments, loginTimeOut, actionTimeOut):
        self.username = username
        self.password = password
        self.departments = departments
        self.loginTimeOut = loginTimeOut
        self.actionTimeOut = actionTimeOut
        self.browser = webdriver.Chrome()

    def login(self):
        browser = self.browser
        password = self.password
        username = self.username
        browser.get("https://act.ucsd.edu/webreg2/start")

        # find username entry and fill 
        username_entry = browser.find_element(By.ID,'ssousername')
        username_entry.clear()
        username_entry.send_keys(username)

        # find password entry and fill
        password_entry = browser.find_element(By.ID,'ssopassword')
        password_entry.clear()
        password_entry.send_keys(password)

        login_button = browser.find_element(By.CSS_SELECTOR,'button[class="btn btn-primary pull-right sso-button"]')
        login_button.click()

        # check if login is successful, if not quit program
        try:
            WebDriverWait(browser,timeout = 10).until(EC.presence_of_element_located((By.ID, '_login_error_message')))
            os._exit()
        except:
            logging.info("correct password")

        
        print("Please check two factor login")

        #if term start button exist, continue, else quit program
        try:
            WebDriverWait(browser, self.loginTimeOut).until(EC.presence_of_element_located((By.ID, 'startpage-button-go'))).click()
        except:
            logging.error(browser.current_url)
            logging.error("can't find terms")
            os._exit(0)

    def click_all_drop_list(self):
        try:
            while True:
                drop_lists =  WebDriverWait(self.browser, self.actionTimeOut).until(EC.presence_of_element_located((By.CSS_SELECTOR,\
            '[class="ui-icon ui-icon-circlesmall-plus tree-wrap-ltr"]')))
                drop_lists.click()
        except TimeoutException:
            logging.info("no more clickable classes")


    def store_file(self,department,pageNum):
        browser = self.browser
        file_name = department + str(pageNum) + '.html'
        
        # delete previous file
        if os.path.exists(os.path.join(os.getcwd(), file_name)):
            os.remove(os.path.join(os.getcwd(), file_name))
        
        # store new file
        file = open(os.path.join(os.getcwd(), file_name),'w')
        file.write(browser.page_source)
        file.close()


    def scrape(self, department):
        browser = self.browser
        # find search bar, if can't find, quit program
        try:
            search_box = WebDriverWait(browser, self.actionTimeOut).until(EC.presence_of_element_located((By.ID,'s2id_autogen1')))
        except:
            logging.error("cannot find search bar")
            os._exit(0)

        #search department
        search_box.clear()
        search_box.send_keys(department + "\n")

        # try to find department, if nothing, quit the function
        try:
            WebDriverWait(browser, self.actionTimeOut).until(EC.presence_of_element_located((By.CSS_SELECTOR,'ul[class=jPag-pages]')))
        except:
            logging.error("no course in such department")
            return

        page_navi = browser.find_element(By.CSS_SELECTOR,'ul[class=jPag-pages]')

        pages = page_navi.find_elements(By.CSS_SELECTOR, 'li')

        for page in pages:
            cur_page = None
            # if the current page is clicked
            try:
                cur_page = page.find_element(By.CSS_SELECTOR, 'span[class="jPag-current"]').text
            except:
                page.find_element(By.TAG_NAME, 'a').click()
                cur_page = page.find_element(By.CSS_SELECTOR, 'span[class="jPag-current"]').text
            
            self.click_all_drop_list(self)
            self.store_file(self,department,cur_page)

    #scape all departments
    def scrape_all(self):
        self.login(self)
        for department in self.departments:
            self.scrape(self, department)

