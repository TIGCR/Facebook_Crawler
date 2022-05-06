import pandas as pd
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
import re
import os
import logging
from datetime import datetime
import json
import random

#取得登入cookie
def get_fb_cookie(email:str, password:str): 
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument('--headless')
    driver = webdriver.Chrome(options=chromeOptions)
    driver.get('https://www.facebook.com/')
    driver.find_element_by_css_selector('#email').send_keys(email)
    driver.find_element_by_css_selector("input[type='password']").send_keys(password)
    driver.find_element_by_css_selector("button[name='login']").click()
    time.sleep(2)
    cookies = driver.get_cookies()
    s = requests.Session()
    #將cookies放入session中
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    driver.quit()
    return s
#日期處理
def Datetime_proccessing(x):
    try:
        if '年' in x:
            try:
                return datetime.strptime(x, "%Y年%m月%d日"+ re.findall(('日(.)午'), x)[0] +"午%I:%M")
            except:
                return datetime.strptime(x, "%Y年%m月%d日").date()
        else:
            try:
                return  datetime.strptime('%d年' % datetime.today().year + x, "%Y年%m月%d日"+ re.findall(('日(.)午'), x)[0] +"午%I:%M")
            except:
                return datetime.strptime('%d年' % datetime.today().year + x, "%Y年%m月%d日").date()
    except:
        return(datetime.today().date())

def GET_content(postid_list,pageid,email,password):
    '''
    postid 要爬的文章，要list形式
    pageid=page_id (可用之前的程式抓)
    
    '''
    s=get_fb_cookie(email=email,password=password)
    #logging.getLogger("requests").setLevel(logging.DEBUG)
    #logging.basicConfig(filename='PageID%s.log' % pageid, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S', level=logging.INFO)
    dfs=[]
    t=0
    for postid in postid_list:
        pageid=pageid
        URL="https://mbasic.facebook.com/story.php?story_fbid="+str(postid)+"&id="+str(pageid)

        headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            # 'cookie': 'datr=PXoIYkiVwJPW6h_p6GRnOf-F; sb=PXoIYuRXOyeT1NEKMA7f2Xic; locale=zh_TW; c_user=100076846151742; xs=37%3Azwb7XYmCO57IhQ%3A2%3A1644729242%3A-1%3A-1; fr=0SmbvcdMgwarFWGAU.AWX0HP_C4Hwu8crCJrBq7x5CJkY.BiCHp_.q6.AAA.0.0.BiCJOZ.AWVwd6hgXrs; m_pixel_ratio=1.100000023841858; x-referer=eyJyIjoiL2hvbWUucGhwIiwiaCI6Ii9ob21lLnBocCIsInMiOiJtIn0%3D; wd=855x792',
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
        response = s.get(URL, headers=headers)
        soup = BeautifulSoup(response.text, features="lxml")
        try:
            pagename = soup.find('strong').text #粉專名稱
        except:
            pagename='抓不到'
        try:
            posttime = Datetime_proccessing(soup.find('abbr').text) #貼文時間
        except:
            posttime='抓不到'
        try:
            context=soup.find('title').text
            texts=soup.find('script').contents[0]
            texts2=texts.split('commentCount":')[1]
            i=0
            d=''
            while d!=',':
                d=texts2[i]
                i+=1
            try:
                COMMENTCOUNT=int(texts2[0:i-1])
            except:
                COMMENTCOUNT=texts2[0:i-1]
            text3=texts.split('LikeAction","userInteractionCount":')[1]
            i=0
            d=''
            while d!='}':
                d=text3[i]
                i+=1
            try:
                REACTIONCOUNT=int(text3[0:i-1])
            except:
                REACTIONCOUNT=text3[0:i-1]
            text4=texts.split('ShareAction","userInteractionCount":')[1]
            i=0
            d=''
            while d!='}':
                d=text4[i]
                i+=1
            try:
                SHARECOUNT=int(text4[0:i-1])
            except:
                SHARECOUNT=text4[0:i-1]
        except:
            context='抓不到'
            COMMENTCOUNT='抓不到'
            REACTIONCOUNT=0
            SHARECOUNT='抓不到'
        concat_df = pd.DataFrame()
        concat_df['URL']=URL
        concat_df['POST_ID']=[postid]
        concat_df['NAME']=[pagename]
        concat_df['TIME']=[posttime]
        concat_df['CONTENT']=[context]
        concat_df['COMMENTCOUNT']=[COMMENTCOUNT]
        concat_df['REACTIONCOUNT']=[REACTIONCOUNT]
        concat_df['SHARECOUNT']=[SHARECOUNT]
        page = 0
        breaktime = 0
        URL='https://mbasic.facebook.com/ufi/reaction/profile/browser/fetch/?ft_ent_identifier='+str(postid)+'&limit=10&total_count='+str(REACTIONCOUNT)
        headers2 = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',

                #'cache-control': 'max-age=0',
                # 'cookie': 'datr=PXoIYkiVwJPW6h_p6GRnOf-F; sb=PXoIYuRXOyeT1NEKMA7f2Xic; locale=zh_TW; c_user=100076846151742; xs=37%3Azwb7XYmCO57IhQ%3A2%3A1644729242%3A-1%3A-1; fr=0SmbvcdMgwarFWGAU.AWX0HP_C4Hwu8crCJrBq7x5CJkY.BiCHp_.q6.AAA.0.0.BiCJOZ.AWVwd6hgXrs; m_pixel_ratio=1.100000023841858; x-referer=eyJyIjoiL2hvbWUucGhwIiwiaCI6Ii9ob21lLnBocCIsInMiOiJtIn0%3D; wd=855x792',
                'referer': 'https://mbasic.facebook.com/mohw.gov.tw/?refid=52&__tn__=C-R',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}
        response2 = s.get(URL,headers=headers2)
        soup2 = BeautifulSoup(response2.text, features="lxml")
        react=soup2.find('div',{'class':'y'})
        reacts_text=react.find_all('a')
        react_dict={}
        for i in reacts_text[1:]:
            marks=i.find('img')['alt']
            num=int(i['href'][i['href'].rfind('=')+1:])
            react_dict[marks]=num
        try:
            LIKE=react_dict['讚']
        except:
            LIKE=0
        try:
            HAHA=react_dict['哈']
        except:
            HAHA=0
        try:
            ANGER=react_dict['怒']
        except:
            ANGER=0
        try:
            LOVE=react_dict['大心']
        except:
            LOVE=0
        try:
            SORRY=react_dict['嗚']
        except:
            SORRY=0
        try:
            SUPPORT=react_dict['加油']
        except:
            SUPPORT=0
        try:
            WOW=react_dict['哇']
        except:
            WOW=0
        concat_df['REACTIONCOUNT']= (ANGER+HAHA+LIKE+LOVE+SORRY+SUPPORT+WOW)
        concat_df['ANGER']=[ANGER]
        concat_df['HAHA']=[HAHA]
        concat_df['LIKE']=[LIKE]
        concat_df['LOVE']=[LOVE]
        concat_df['SORRY']=[SORRY]
        concat_df['SUPPORT']=[SUPPORT]
        concat_df['WOW']=[WOW]
        dfs.append(concat_df)
        t+=1
        print(f'全部：{len(postid_list)}\n完成文章:{t}')
        time.sleep(random.choice([3,5,6,7,10]))
    print('爬蟲完成')
    return dfs
'''
參數說明：
1. postid_list：貼文id(list形式)
2. pageid_list_list：專頁id(list形式)
3. email=facebook帳號
4.password=facebook密碼
'''
email=''
password=''
id_list=pd.read_excel('POSTID&PAGEID.xlsx')
##len(id_list)
#id_list=id_list.drop_duplicates()
#id_list=id_list.reset_index()[90:]
postid_list=id_list['POSTID']
pageid=id_list['PAGEID'][0]
df=GET_content(postid_list,pageid,email,password)
df2=pd.concat(df)
df2['PAGEID']=pageid
df2.to_excel('貼文內容.xlsx',index=False)



