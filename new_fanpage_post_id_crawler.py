# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
import re
import os
import logging
from datetime import datetime,timedelta,date
import json
import random
def get_fb_cookie(email:str, password:str): 
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument('--headless')
    driver = webdriver.Chrome(options=chromeOptions)
    driver.get('https://www.facebook.com/')
    driver.find_element(By.CSS_SELECTOR,"#email").send_keys(email)
    driver.find_element(By.CSS_SELECTOR,"input[type='password']").send_keys(password)
    driver.find_element(By.CSS_SELECTOR,"button[name='login']").click()
   
    time.sleep(2)
    
    cookies = driver.get_cookies()
   
    s = requests.Session()
    #將cookies放入session中
    
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    driver.quit()
    return s
def get_time(x):
    time_list=x.find_all('abbr')
    Time_list=[]
    for i in time_list:
        try:
            try:
                Time = i.text
                Time=re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)',Time).group()
                Time = datetime.strptime(Time,  '%Y年%m月%d日')
                Time = Time.strftime("%Y-%m-%d").date()
            except:
                Time=i.text
                Time='2022年'+Time
                Time=re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)',Time).group()
                Time = datetime.strptime(Time,  '%Y年%m月%d日')
                Time = Time.strftime("%Y-%m-%d")
                Time =datetime.strptime(Time,'%Y-%m-%d').date()
        except:
            Time = date.today()
        Time_list.append(Time)
    return Time_list
def get_post_id(x):
    
    t1=x.find_all('div',{'class':'_55wo _56bf _5rgl'})
    if len(t1)<1:
        t1=x.find_all('div',{'class':'bl bm bn'})
    id_list=[]
    for i in t1:
        try:
            id_list.append(re.search(r'"top_level_post_id":"(\d{1,20})',i['data-ft']).group().replace('"top_level_post_id":"',''))
        except:
            pass
    
    return id_list
def get_next_page(x):
    url3=0
    a=x.find_all('a')
    while type(url3)==int:
        try:
            if a[url3].text=='查看更多動態':
                url3='https://mbasic.facebook.com/'+a[url3]['href']
            else:
                url3+=1
        except:
            url3+=1
            pass
    return url3
def get_PAGEID(x):
    headers = {'accept': 'text/html',
                   'sec-fetch-user': '?1'}
    rs = requests.Session()
    content_df = [] # post
    feedback_df = [] # reactions
    timeline_cursor = ''
    max_date =  datetime.now().strftime('%Y-%m-%d')
    break_times = 0
    pageurl=x
        # Get PageID
    resp = rs.get(pageurl, headers=headers)
    try:
        pageid = re.findall('page_id=(.*?)"',resp.text)[0]
    except:
        pageid = re.findall('delegate_page":\{"id":"(.*?)"\},', resp.text)[0]
    return pageid
def crawl_post_id(email,password,url,until_date):
    until_date=datetime.strptime(until_date,'%Y-%m-%d').date()
    s=get_fb_cookie(email=email,password=password)
    headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
 'accept-encoding': 'gzip, deflate, br',
 'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
 'cache-control': 'max-age=0',
 'referer': 'https://mbasic.facebook.com/mohw.gov.tw/?refid=52&__tn__=C-R',
 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
 'sec-ch-ua-mobile': '?0',
 'sec-ch-ua-platform': '"Windows"',
 'sec-fetch-dest': 'document',
 'sec-fetch-mode': 'navigate',
 'sec-fetch-site': 'same-origin',
 'sec-fetch-user': '?1',
 'upgrade-insecure-requests': '1',
 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}
    dates=date.today()
    fan_page_name=re.search(r'.com/(\S{1,100})',url).group().replace('.com/','')
    response=s.get(f'https://mbasic.facebook.com/{fan_page_name}',headers=headers)
    soup = BeautifulSoup(response.text, features="lxml")
    for i in soup.find_all('a'):
        if i.text=='動態時報':
            tar=i['href']
    url2='https://mbasic.facebook.com'+tar
    print(f'粉絲專業名稱：{fan_page_name}')
    time.sleep(3)
    post_id_list=[]
    while dates > until_date:
        response=s.get(url2)
        soup = BeautifulSoup(response.text, features="lxml")
        ids=get_post_id(soup)
        for i in ids:
            post_id_list.append(i)
        TIMES=get_time(soup)
        dates=TIMES[-1]
        url2=get_next_page(soup)
        print(f'爬到:{dates}\n 已爬：{len(post_id_list)}貼文')
        #else:
            #date=datetime.datetime.strptime(date,  '%Y-%m-%d-')
        time.sleep(random.choice([i for i in range(3, 8)]))
        
    #soups = BeautifulSoup(driver.page_source)
    return post_id_list

email=''
password=''
url='URL of FB Fan page'
#until_date is the approximate date for stop scraping
post_IDs=crawl_post_id(email=email,password=password,url=url,until_date='2022-06-01')

df=pd.DataFrame(post_IDs,columns=['POSTID'])
df=df.drop_duplicates()
df['PAGEID']=get_PAGEID(url)
df.to_excel('POSTID&PAGEID.xlsx',index=False)