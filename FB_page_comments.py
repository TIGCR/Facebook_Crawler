# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 20:52:29 2021

@author: User
"""
import pandas as pd
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
def get_cookie():
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument('--headless')
    driver = webdriver.Chrome(options=chromeOptions)
    driver.get('https://www.facebook.com/')
    driver.find_element_by_css_selector('#email').send_keys('tigcr.nccu.gis@gmail.com')
    driver.find_element_by_css_selector("input[type='password']").send_keys('fbbad1234!')
    driver.find_element_by_css_selector("button[name='login']").click()
    time.sleep(2)
    cookies = driver.get_cookies()
    s = requests.Session()
    #將cookies放入session中
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    driver.quit()
    return s

def find_tag(s, URL, headers):
    response = s.get(URL, headers=headers)
    if response.status_code == 200:
        print("status：200")
    soup = BeautifulSoup(response.text)
    tag_dict = {}
    for tag in ["ej", "el", "ei", "by","en"]:
        n = 0
        table = soup.find_all("div", class_=tag)
        for i in range(len(table)):
            if "讚 · 傳達心情 · 回覆 · 更多" in table[i].get_text():
                n += 1
        tag_dict[tag] = n
    return max(tag_dict, key=tag_dict.get)


def fb_page_comment_crawler(s, postid_list):
    columns = ["postid", "source", "date", "comment", "reactions"]
    res_dict = {i:[] for i in columns}
    for postid in postid_list:
        URL = "https://mbasic.facebook.com/story.php?story_fbid="+postid+"&id=470265436473213"
        headers ={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        nextpage, previouspage = True, False
        tag = find_tag(s, URL, headers)
        while nextpage:
            response = s.get(URL, headers=headers)
            # time.sleep(1)
            if response.status_code == 200:
                print("status：200")
            soup = BeautifulSoup(response.text)
            table = soup.find_all("div", class_=tag)
            try:
                if table[-1].find("div"):
                    nextpage = False
                else:
                    URL = "https://mbasic.facebook.com" + table[-1].find("a").get('href')
                    print("---next page exists")
            except IndexError:
                if not table:
                    nextpage = False
            for i in range(previouspage, len(table)-nextpage):
                content = table[i].find_all("div")
                if len(content) > 3:
                    res_dict["postid"].append(postid)
                    res_dict["source"].append(table[i].find("h3").get_text())
                    if content[2].find("img"):
                        res_dict["comment"].append(content[1].get_text()+content[2].get_text()+"圖片網址："+content[2].find("img").get('src'))
                    else:
                        res_dict["comment"].append(content[1].get_text()+content[2].get_text())
                    
                    for j in range(3, len(content)):
                        if "讚 · 傳達心情 · 回覆 · 更多" in content[j].get_text():
                            other = content[j].get_text().split(" · ")
                            res_dict["date"].append(other[-1])
                            if other[0].isdigit():
                                res_dict["reactions"].append(int(other[0]))
                            else:
                                res_dict["reactions"].append(0)
                            break
                else:
                    continue
            previouspage = True
        print("---postid：",postid, "Done!")
    return res_dict
  
#執行
s = get_cookie()
postid_list = [i.split("/")[-1] for i in pd.read_csv("衛生福利部.csv").url]
test = fb_page_comment_crawler(s, postid_list) 
res = pd.DataFrame(test)
res.to_csv("衛生福利部貼文留言.csv", encoding = "utf-8-sig")
