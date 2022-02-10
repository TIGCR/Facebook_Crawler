import requests
import re
import json
from bs4 import BeautifulSoup
import time
import datetime
import pandas as pd

# Fans page ==================================================================
## parse_content
def parse_content(data):
    df = []
    soup = BeautifulSoup(data['domops'][0][3]['__html'], 'lxml')
    # post
    for ele in soup.findAll('div', {'class':'userContentWrapper'}):
        content = ele.find('div', {'data-testid':'post_message'})
        try:
            content = ''.join(p.text for p in content.findAll('p'))
        except:
            content = ''
            
        df.append([
            ele.find('img')['aria-label'], # name
            ele.find('div', {'data-testid':'story-subtitle'})['id'], # id
            ele.find('abbr')['data-utime'], #time
            content, # content
            ele.find('a')['href'].split('?')[0] #link
            ]) 
    df = pd.DataFrame(data=df, columns=['NAME', 'ID', 'TIME', 'CONTENT', 'LINK'])
    df['PAGEID'] = df['ID'].apply(lambda x: re.findall('[0-9]{5,}', x)[0])
    df['POSTID'] = df['ID'].apply(lambda x: re.findall('[0-9]{5,}', x)[1])
    df['TIME'] = df['TIME'].apply(lambda x: datetime.datetime.fromtimestamp(int(x)).strftime("%Y-%m-%d %H:%M:%S"))
    df = df.drop('ID',axis=1)
    return df

## get_reaction
def get_reaction(data):
    df = []
    # posts
    for ele in data['jsmods']['pre_display_requires']:
        try:
            df.append([
                ele[3][1]['__bbox']['result']['data']['feedback']['subscription_target_id'], # post id
                ele[3][1]['__bbox']['result']['data']['feedback']['owning_profile']['id'], # page id
                ele[3][1]['__bbox']['result']['data']['feedback']['display_comments_count']['count'],  # display_comments_count
                ele[3][1]['__bbox']['result']['data']['feedback']['comment_count']['total_count'], # total_comments_count
                ele[3][1]['__bbox']['result']['data']['feedback']['reaction_count']['count'], # reaction_count
                ele[3][1]['__bbox']['result']['data']['feedback']['share_count']['count'], # share_count
                ele[3][1]['__bbox']['result']['data']['feedback']['top_reactions']['edges'], # reactions
            ])
        except:
            pass
    
    # vidoes
    for ele in data['jsmods']['require']:
        try:            
            df.append([
                    ele[3][2]['feedbacktarget']['entidentifier'], # post id
                    ele[3][2]['feedbacktarget']['actorid'], # page id
                    ele[3][2]['feedbacktarget']['commentcount'], # comment count
                    ele[3][2]['feedbacktarget']['likecount'], # reaction count
                    ele[3][2]['feedbacktarget']['sharecount'], # sharecount
                    ele[3][2]['feedbacktarget']['commentcount'], # display_comments_count
                    [] # reactions
            ])
        except:
            pass
    df = pd.DataFrame(df, columns=['POSTID', 'PAGEID', 'COMMENTCOUNT', 'REACTIONCOUNT', 'SHARECOUNT', 'DISPLAYCOMMENTCOUNT', 'REACTIONS'])
    reaction_df = df.loc[:,['PAGEID', 'POSTID', 'REACTIONS']].explode('REACTIONS')
    reaction_df = reaction_df.loc[reaction_df['REACTIONS'].notnull()]
    reaction_df['COUNT'] = reaction_df['REACTIONS'].apply(lambda x: x['reaction_count'])
    reaction_df['TYPE'] = reaction_df['REACTIONS'].apply(lambda x: x['node']['reaction_type'])
    reaction_df = reaction_df.drop_duplicates(['PAGEID', 'POSTID', 'TYPE'], keep='first')
    reaction_df = reaction_df.pivot(index=['PAGEID', 'POSTID'], columns='TYPE', values='COUNT').reset_index()
    return reaction_df

# Crawl_PagePosts
def Crawl_PagePosts(pageurl, until_date='2019-01-01'):
    
    # init parameters
    headers = {'accept': 'text/html',
               'sec-fetch-user': '?1'}
    rs = requests.Session()
    content_df = [] # post
    feedback_df = [] # reactions
    timeline_cursor = ''
    max_date =  datetime.datetime.now().strftime('%Y-%m-%d')
    break_times = 0
    
    # Get PageID
    resp = rs.get(pageurl, headers=headers)
    try:
        pageid = re.findall('page_id=(.*?)"',resp.text)[0]
    except:
        pageid = re.findall('delegate_page":\{"id":"(.*?)"\},', resp.text)[0]

    # request date and break loop when reach the goal 
    while max_date >= until_date:
        
        # request params
        url = 'https://www.facebook.com/pages_reaction_units/more/'
        params = {'page_id': pageid,
                  'cursor': str({"timeline_cursor":timeline_cursor,
                                 "timeline_section_cursor":'{}',
                                 "has_next_page":'true'}), 
                  'surface': 'www_pages_home',
                  'unit_count': 20,
                  '__a': '1'}

        try:
            resp = rs.get(url, params=params)
            data = json.loads(re.sub(r'for \(;;\);','',resp.text)) # \(\) 表示不為一個group只是'('
            
            # contesnts：poster's name, poster's ID, post ID, time, content
            ndf = parse_content(data=data)
            content_df.append(ndf)

            # reactions
            ndf1 = get_reaction(data=data)
            feedback_df.append(ndf1)
  
            # update request params
            max_date = ndf['TIME'].max()
            print('TimeStamp: {}.'.format(ndf['TIME'].max()))
            timeline_cursor = re.findall(r'timeline_cursor\\u002522\\u00253A\\u002522(.*?)\\u002522\\u00252C\\u002522timeline_section_cursor',resp.text)[0]
            # break times to zero
            break_times = 0

        except:
            break_times += 1
            print('break_times:', break_times)
        
        time.sleep(2)
        if break_times > 5:
            break
    
    # join content and reactions
    content_df = pd.concat(content_df, ignore_index=True)
    feedback_df = pd.concat(feedback_df, ignore_index=True)
    df = pd.merge(left=content_df, right=feedback_df, how='left', on=['PAGEID', 'POSTID'])
    df = df.fillna(value={'ANGER':0, 'HAHA':0, 'LIKE': 0, 'LOVE':0, 'SORRY':0, 'SUPPORT':0, 'WOW': 0}) 
    df['UPDATETIME'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")      
    print('There are {} posts in DataFrame.'.format(str(df.shape[0])))
    return df

# def get_postid(pageurl, until_date='2019-01-01'):
#     pageid = get_pageid(pageurl) 

#     content_df = [] # post
#     feedback_df = [] # reactions
#     timeline_cursor = ''
#     max_date =  datetime.datetime.now()
#     break_times = 0
    
#     # request date and break loop when reach the goal 
#     while max_date >= datetime.datetime.strptime(until_date, '%Y-%m-%d'):
        
#         # request params
#         url = 'https://www.facebook.com/pages_reaction_units/more/'
#         params = {'page_id': pageid,
#                   'cursor': str({"timeline_cursor":timeline_cursor,
#                                   "timeline_section_cursor":'{}',
#                                   "has_next_page":'true'}), 
#                   'surface': 'www_pages_home',
#                   'unit_count': 20,
#                   '__a': '1'}

#         try:
#             resp = requests.get(url, params=params)
#             data = json.loads(re.sub(r'for \(;;\);','',resp.text)) # \(\) 表示不為一個group只是'('
            
#             # contesnts：poster's name, poster's ID, post ID, time, content
#             ndf = parse_content(data=data)
#             content_df.append(ndf)

#             # reactions
#             ndf1 = get_reaction(data=data)
#             feedback_df.append(ndf1)
  
#             # update request params
#             max_date = ndf['TIME'].max()
#             print('TimeStamp: {}.'.format(ndf['TIME'].max()))
#             timeline_cursor = re.findall(r'timeline_cursor\\u002522\\u00253A\\u002522(.*?)\\u002522\\u00252C\\u002522timeline_section_cursor',resp.text)[0]
#             # break times to zero
#             break_times = 0

#         except:
#             break_times += 1
#             print('break_times:', break_times)
        
#         time.sleep()
#         if break_times > 5:
#             break
    
#     # join content and reactions
#     content_df = pd.concat(content_df, ignore_index=True)
#     feedback_df = pd.concat(feedback_df, ignore_index=True)
#     df = pd.merge(left=content_df, right=feedback_df, how='left', on=['PAGEID', 'POSTID'])
#     df = df.loc[:,['NAME', 'TIME', 'CONTENT', 'PAGEID', 'POSTID', 'display_comments_count', 'total_comments_count', 'reaction_count', 'share_count', 'LIKE', 'LOVE', 'HAHA', 'SUPPORT', 'WOW', 'ANGER', 'SORRY']]
#     df = df.rename(columns={'display_comments_count':'DISPLAYCOMMENTS', 'total_comments_count':'TOTAL_COMMENTS', 'reaction_count':'REACTIONS','share_count':'SHARES'})
#     df['UPDATETIME'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")      
#     df['url'] = df['POSTID'].apply(lambda x: pageurl+'/posts/'+x)
#     print('There are {} posts in DataFrame.'.format(str(df.shape[0])))
#     return df