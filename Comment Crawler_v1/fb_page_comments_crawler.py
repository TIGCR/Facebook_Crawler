import pandas as pd
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
import re
import os
import logging
from datetime import datetime

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

#爬取內容
def parse_content(response):   
    columns = ["PageName" ,"PageID", "PostID", "PostTime", "PostURL","CommentID","Comment", "Time", "Reactions", "Replies","AuthorName", "AuthorProfileURL", "Replies_URL"]
    res_dict = {i:[] for i in columns}
    
    tagnid = get_commentID(response)
    soup = BeautifulSoup(response.text, features="lxml")
    for i in tagnid:
        target = soup.find('div', {'id':i[1]})
        authorinfo = target.find('h3')
        content = target.find_all('div')
        n_replies = re.findall(r'已回覆 · (\d+) 則回覆', target.get_text())
        nlikes = target.find('span', {'id':re.findall(r'id="(like_\d+_\d+)"', str(target))}).text.split()[0]
        
        res_dict['PageName'].append('')
        res_dict["PageID"].append('')
        res_dict["PostID"].append('')
        res_dict["PostTime"].append('')
        res_dict["PostURL"].append('')
        
        res_dict["CommentID"].append(i[1])
        res_dict["AuthorName"].append(authorinfo.get_text())
        res_dict["AuthorProfileURL"].append('https://facebook.com'+authorinfo.find('a').get('href'))
        res_dict["Time"].append(Datetime_proccessing(content[0].find("abbr").get_text()))
        
        try:
            res_dict["Comment"].append(''.join([content[1].get_text(), 
                                                content[2].get_text(), 
                                                '<圖片>'+content[2].find('img').get('alt')]))
        except:
            res_dict["Comment"].append(''.join([content[1].get_text(), 
                                                content[2].get_text()]))
            
        
        if nlikes.isdigit():
            res_dict["Reactions"].append(nlikes)
        else:
            res_dict["Reactions"].append("0")

        
        
        if n_replies:
            res_dict['Replies'].append(n_replies[0])
            res_dict['Replies_URL'].append('https://mbasic.facebook.com' + content[-1].find('a').get('href'))

        else:
            res_dict['Replies'].append('0')
            res_dict['Replies_URL'].append('')
            
    return pd.DataFrame(res_dict)

    
#取得留言id定位                
def get_commentID(response):
    
    return re.findall(r'<div class="(\w+)" id="(\d+)"', response.text)


def fb_page_comment_crawler(s, postid_list, pageid, nested = False):
    '''
    留言將自動存入對應資料夾
    
    Parameters
    ----------
    s : requests.sessions.Session
        包含登入cookie的sessions
    postid_list : list
        欲爬取的貼文ID列表
    pageid : str
        欲爬取的粉專ID
    nested : bool, default False
        是否開啟巢狀留言爬取

    Returns None
    -------

    '''
        
    logging.getLogger("requests").setLevel(logging.DEBUG)
    logging.basicConfig(filename='PageID%s.log' % pageid, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S', level=logging.INFO)
    
    for postid in postid_list:
        URL = "https://mbasic.facebook.com/story.php?story_fbid="+postid+"&id="+pageid
        
        headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
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
        pagename = soup.find('strong').text #粉專名稱
        posttime = Datetime_proccessing(soup.find('abbr').text) #貼文時間
        concat_df = []
        concat_df_nested = []
        page = 0
        breaktime = 0
        
        #建立粉專資料夾
        if not os.path.exists("粉專留言/"+pagename):
            os.mkdir("粉專留言/"+pagename)
        
        try:
            #爬取Display comment
            while True:
                
                if soup.find('title').get_text() == '你暫時遭到封鎖':
                    print('暫時被封鎖\nPageid:%s\nPostid:%s'%(pageid, postid))
                    logging.error('\t功能暫時被封鎖')
                    return None
                
                if len(get_commentID(response)):
                    
                    concat_df.append(parse_content(response))
                    
                    page += 10
                    response = s.get("&".join([URL, "p=%d" % page]), headers=headers)
                    soup = BeautifulSoup(response.text, features="lxml")
                    
                else:
                    if concat_df:
                        df1 = pd.concat(concat_df, axis = 0, ignore_index = True)
                        print('%s PostID:%s\nDisplay Comments:%d' % (pagename, postid, len(df1)))
                        #爬取Nested comment
                        if nested:
                            Replies_URLs = [i for i in df1['Replies_URL'].to_list() if i != '']
                            if Replies_URLs:            
                                for Replies_URL in Replies_URLs:
                                    rURL = Replies_URL
                                    nextpage = True
                                    while nextpage:
                                        response = s.get(rURL, headers=headers)
                                        soup = BeautifulSoup(response.text, features="lxml")
                                        concat_df_nested.append(parse_content(response))
                                        try:
                                            nextpage_buttom = soup.find('div', {'id':re.findall(r'id="(comment_replies_more_1:\d+?_\d+?)">', response.text)[0]})
                                            rURL = 'https://mbasic.facebook.com' + nextpage_buttom.find('a').get('href')
                                        except:
                                            nextpage = False
                        
                        df = pd.concat([df1]+concat_df_nested, axis = 0, ignore_index = True)
                        df['PageName'] = pagename
                        df["PageID"] = pageid
                        df["PostID"] = postid
                        df["PostTime"] = posttime
                        df["PostURL"] = URL
                        
                        #匯出留言檔
                        df.to_csv("粉專留言/"+pagename+'/PostID%s.csv' % postid, encoding = 'utf-8-sig', index=False)
                        print('Total Comments:%d\n' % (len(df["Comment"])))
                        logging.info(' PostID:%s Total Comments:%d' %(postid, len(df["Comment"])))
                        break
                    
                    else:
                        print('%s PostID:%s\nTotal Comments:%d\n' % (pagename, postid, 0))
                        logging.info(' PostID:%s Total Comments:%d' %(postid, 0))
                        break

        except:
                breaktime +=1
                print('breaktime=%d' % breaktime)
                logging.exception('Error Occured：\n')
                if breaktime > 6:
                    break







