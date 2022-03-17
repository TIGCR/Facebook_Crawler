from bs4 import BeautifulSoup
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import requests, gc, os
import re
import math
import pandas as pd
import numpy as np
import datetime
from selenium.webdriver.common.action_chains import ActionChains #move_to_element
from selenium.common.exceptions import StaleElementReferenceException #error > element is not attached to the page document
from selenium.common.exceptions import NoSuchElementException #點完所有按鈕時
import random

def log_in(email,password):
    '''
    輸入Facebook的email和密碼，如:
    email='12345@gmail.com'
    passowrd='1234567'
    '''
    driver.get('https://www.facebook.com/')
    input_1 = driver.find_element_by_css_selector('#email')
    input_2 = driver.find_element_by_css_selector("input[type='password']")

    input_1.send_keys('email')
    input_2.send_keys('password')
    driver.find_element_by_css_selector("button[name='login']").click()
    time.sleep(1)
def get_link(i):
    Link_list=i.find_all('li',{'class':'h676nmdw oi9244e8 q9uorilb'})
    Link=[]
    for i in Link_list:
        try:
            t=i.find('a')['href']
            Link.append(t)
        except:
            pass
    return Link
def get_time(x):
    time_list=x.find_all('a',{'class':'oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw'})
    Time_list=[]
    for i in time_list:
        try:
            try:
                Time = i['aria-label']
                Time = datetime.datetime.strptime(Time,  '%Y年%m月%d日')
                Time = Time.strftime("%Y-%m-%d")
            except:
                Time=i['aria-label']
                Time='2022年'+Time
                Time = datetime.datetime.strptime(Time,  '%Y年%m月%d日')
                Time = Time.strftime("%Y-%m-%d")
                Time =datetime.datetime.strptime(Time,'%Y-%m-%d')
        except:
            Time = 'Not Post'
        Time_list.append(Time)
    return Time_list
def get_POST_ID(x):
    POST_ID_LIST=[]
    for i in x:
        postid=i.split('posts/')[1][0:15]
        POST_ID_LIST.append(postid)
    return POST_ID_LIST
def crawl_postid (url,until_date):
    '''
    url:欲爬的網址
    until_date:爬到幾月幾號(只能爬抽過一個月)，格式:'2022-01-01'
    '''
    driver.get(url)
    until_date=datetime.datetime.strptime(until_date,'%Y-%m-%d')
    date=datetime.datetime.now()
    scroll_top=0 #滾輪
    time.sleep(5)
    while date > until_date:
        for i in range(0,10):
            scroll_top+=500
            js=f"var action=document.documentElement.scrollTop={scroll_top}"
            driver.execute_script(js)
            time.sleep(1)
        soup = BeautifulSoup(driver.page_source)
        LINKS=get_link(soup)
        TIMES=get_time(soup)
        date=TIMES[-1]
        if date=='Not Post':
            date=datetime.datetime.now()
        #else:
            #date=datetime.datetime.strptime(date,  '%Y-%m-%d-')
        time.sleep(random.choice([i for i in range(3, 8)]))
    LINK=get_link(soup)[1:]
    POST_IDS=get_POST_ID(LINK)
    return POST_IDS
def get_page_id(x):
    headers = {'accept': 'text/html',
                   'sec-fetch-user': '?1'}
    rs = requests.Session()
    content_df = [] # post
    feedback_df = [] # reactions
    timeline_cursor = ''
    max_date =  datetime.datetime.now().strftime('%Y-%m-%d')
    break_times = 0
    pageurl=x
        # Get PageID
    resp = rs.get(pageurl, headers=headers)
    try:
        pageid = re.findall('page_id=(.*?)"',resp.text)[0]
    except:
        pageid = re.findall('delegate_page":\{"id":"(.*?)"\},', resp.text)[0]
    return pageid
driver = webdriver.Chrome('chromedriver')

email=''
password=''

log_in(email,password)
# URL of FB Fan Page e.g. https://www.facebook.com/joebiden  https://www.facebook.com/WithGaLoveTaiwan
url='https://www.facebook.com/'

driver.get(url)
# until_date 大約爬貼文id的最早日期 
post_IDs=crawl_postid (url,until_date='2022-02-01')
df=pd.DataFrame(post_IDs,columns=['POSTID'])
df['PAGEID']=get_page_id(url)
# 將爬文的dataframe存成一個excel檔
df.to_excel('POSTID&PAGEID.xlsx')