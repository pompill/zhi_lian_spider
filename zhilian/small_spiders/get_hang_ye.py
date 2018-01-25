from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import requests
import json
import re
import pymongo
import time
import redis

browser = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
wait = WebDriverWait(browser, 10)
r = redis.Redis(host='localhost',port=6379,db=0)
def search():
    try:
        browser.get('http://sou.zhaopin.com/jobs/searchresult.ashx')
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#buttonSelIndustry')))
        button.click()
        time.sleep(1)
        # browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        get_industryname()
    except TimeoutException:
        search()
def get_industryname():
    html = browser.page_source
    soup = bs(html,'html.parser')
    if soup.select('.paddingTB .chebox'):
        industryname_all=soup.select('td[class="mOutItem"] label input')
        for i in industryname_all:
            industry_num = i.get('value')
            r.sadd('industry',industry_num)
if __name__=="__main__":
    search()