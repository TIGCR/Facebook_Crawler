import requests
import re
import json
from bs4 import BeautifulSoup
import datetime
import time
import pandas as pd
from dicttoxml import dicttoxml
from lxml import etree
import random

class ServerException(Exception):
    pass

def __get_cookieid__(pageurl):
    '''
    Send a request to get cookieid as headers.
    '''
    pageurl = re.sub('www', 'm', pageurl)
    resp = requests.get(pageurl)
    headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
             'accept-language': 'en'}
    headers['cookie'] = '; '.join(['{}={}'.format(cookieid, resp.cookies.get_dict()[cookieid]) for cookieid in resp.cookies.get_dict()])
    headers['ec-ch-ua-platform'] = 'Windows'
    # headers['cookie'] = headers['cookie'] + '; locale=en_US'
    return headers


def __get_pageid__(pageurl):
    '''
    Send a request to Facebook Server to get the pageid, docid and request name.
    '''
    pageurl = re.sub('/$', '', pageurl)
    headers = __get_cookieid__(pageurl)
    time.sleep(1)

    resp = requests.get(pageurl, headers)
    # pageID
    if len(re.findall('"pageID":"([0-9]{1,})",', resp.text)) >= 1:
        pageid = re.findall('"pageID":"([0-9]{1,})",', resp.text)[0]
    elif len(re.findall(r'"identifier":(.*?),', resp.text)) >= 1:
        pageid = re.findall(r'"identifier":(.*?),', resp.text)[0]
    elif len(re.findall('delegate_page":\{"id":"(.*?)"\},', resp.text)) >= 1:
        pageid = re.findall('delegate_page":\{"id":"(.*?)"\},', resp.text)[0]
    elif len(re.findall('fb://group|page|profile/([0-9]{1,})', resp.text)) >= 1:
        pageid = re.findall('fb://group|page|profile/([0-9]{1,})', resp.text)[0]
    else:
        pageid = ''
    print('{}\'s pageid is: {}'.format(pageurl.split('/', -1)[-1], pageid))

    # postid
    soup = BeautifulSoup(resp.text, 'lxml')
    for js in soup.findAll('link', {'rel': 'preload'}):
        resp = requests.get(js['href'])
        for line in resp.text.split('\n', -1):
            if 'ProfileCometTimelineFeedRefetchQuery_' in line:
                docid = re.findall('e.exports="([0-9]{1,})"', line)[0]
                req_name = 'ProfileCometTimelineFeedRefetchQuery'
                break

            if 'CometModernPageFeedPaginationQuery_' in line:
                docid = re.findall('e.exports="([0-9]{1,})"', line)[0]
                req_name = 'CometModernPageFeedPaginationQuery'
                break

            if 'CometUFICommentsProviderQuery_' in line:
                docid = re.findall('e.exports="([0-9]{1,})"', line)[0]
                req_name = 'CometUFICommentsProviderQuery'
                break
    print('{}\'s docid is: {}'.format(pageurl.split('/', -1)[-1], docid))

    return pageid, docid, req_name


def __parsing_edge__(edge):
    # name
    comet_sections_ = edge['node']['comet_sections']
    name = comet_sections_['context_layout']['story']['comet_sections']['actor_photo']['story']['actors'][0]['name']
    # creation_time
    creation_time = comet_sections_['context_layout']['story']['comet_sections']['metadata'][0]['story']['creation_time']
    # message
    message = comet_sections_['content']['story']['comet_sections'].get('message','').get('story','').get('message','').get('text','') if comet_sections_['content']['story']['comet_sections'].get('message','') else ''
    # postid
    postid = comet_sections_['feedback']['story']['feedback_context']['feedback_target_with_context']['ufi_renderer']['feedback']['subscription_target_id']
    # actorid
    pageid = comet_sections_['context_layout']['story']['comet_sections']['actor_photo']['story']['actors'][0]['id']
    # comment_count
    comment_count = comet_sections_['feedback']['story']['feedback_context']['feedback_target_with_context']['ufi_renderer']['feedback']['comment_count']['total_count']
    # reaction_count
    reaction_count = comet_sections_['feedback']['story']['feedback_context']['feedback_target_with_context']['ufi_renderer']['feedback']['comet_ufi_summary_and_actions_renderer']['feedback']['reaction_count']['count']
    # share_count
    share_count = comet_sections_['feedback']['story']['feedback_context']['feedback_target_with_context']['ufi_renderer']['feedback']['comet_ufi_summary_and_actions_renderer']['feedback']['share_count']['count']
    # toplevel_comment_count
    toplevel_comment_count = comet_sections_['feedback']['story']['feedback_context']['feedback_target_with_context']['ufi_renderer']['feedback']['toplevel_comment_count']['count']
    # top_reactions
    top_reactions = comet_sections_['feedback']['story']['feedback_context']['feedback_target_with_context']['ufi_renderer']['feedback']['comet_ufi_summary_and_actions_renderer']['feedback']['cannot_see_top_custom_reactions']['top_reactions']['edges']
    # cursor
    cursor = edge['cursor']
    # url
    url = comet_sections_['context_layout']['story']['comet_sections']['actor_photo']['story']['actors'][0]['url']

    # attachments
    attachments = get_attachment(comet_sections_)

    self_link = get_selflink(comet_sections_)

    return [name, creation_time, self_link, message, postid, pageid, comment_count, reaction_count, share_count, toplevel_comment_count, top_reactions, cursor, url, attachments]

def get_attachment(comet_sections_):
    xml_data = dicttoxml(comet_sections_, attr_type=False)
    tree = etree.fromstring(xml_data)
    attachments = tree.xpath('//uri/text()')
    return ','.join(attachments)

def get_selflink(comet_sections_):
    xml_data = dicttoxml(comet_sections_, attr_type=False)
    tree = etree.fromstring(xml_data)
    urls = tree.xpath('//url/text()')
    selflink = [link for link in urls if link.endswith("type=3")]
    return ','.join(selflink)


def __parsing_ProfileComet__(resp):
    edge_list = []
    resps = resp.text.split('\r\n', -1)
    for i, res in enumerate(resps):
        # print(i)
        try:
            edge = json.loads(res)['data']['node']['timeline_list_feed_units']['edges'][0]
            edge = __parsing_edge__(edge)
            edge_list.append(edge)
            
        except:
            pass
        try:
            edge = json.loads(res)['data']
            edge = __parsing_edge__(edge)
            edge_list.append(edge)
        except:
            pass

    max_date = max([edge[1] for edge in edge_list])
    max_date = datetime.datetime.fromtimestamp(int(max_date)).strftime('%Y-%m-%d')
    cursor = edge_list[-1][-3] # DANGEROUS
    print('The maximum date of these posts is: {}, {}, keep crawling...'.format(max_date, cursor))
    return edge_list, cursor, max_date

def __parsing_CometModern__(resp):
    edge_list = []
    resp = json.loads(resp.text.split('\r\n', -1)[0])

    for edge in resp['data']['node']['timeline_feed_units']['edges']:
        try:
            edge = __parsing_edge__(edge)
            edge_list.append(edge)
        except Exception as e:
            raise e
        
    max_date = max([edge[1] for edge in edge_list])
    max_date = datetime.datetime.fromtimestamp(int(max_date)).strftime('%Y-%m-%d')
    print('The maximum date of these posts is: {}, keep crawling...'.format(max_date))
    cursor = edge_list[-1][-3] # DANGEROUS
    return edge_list, cursor, max_date

def __extract_reactions__(reactions, reaction_type):
    '''
    Extract reaction_type from reactions.
    Possible reaction_type's value will be one of ['LIKE', 'HAHA', 'WOW', 'LOVE', 'SUPPORT', 'SORRY', 'ANGER'] 
    '''
    for reaction in reactions:
        if reaction['node']['localized_name'].upper() == reaction_type.upper():
            return reaction['reaction_count']
    return 0


def find_json_path(json, path, sep="."):
    path = path.split(sep)

    for key in path:
        json = json.get(key, '')
        if not json:
            return ''
    if json:
        return json
    else:
        return ''


def has_next_page(resp):
    resp = json.loads(resp.text.split('\r\n', -1)[0])

    if resp['data']['node']['timeline_feed_units']:
        has_next_page = resp['data']['node']['timeline_feed_units']['page_info']['has_next_page']
    # elif resp.get('errors'):
    #     raise ServerException("Error from Server")

    return has_next_page


def Crawl_PagePosts(pageurl, until_date='2018-01-01'):
    # init parameters
    contents = []  # post
    cursor = ''
    max_date = datetime.datetime.now().strftime('%Y-%m-%d')
    break_times = 0

    headers = __get_cookieid__(pageurl)
    # Get pageid, postid and reqname
    pageid, docid, req_name = __get_pageid__(pageurl)

    # request date and break loop when reach the goal 
    while max_date >= until_date:
        # Rate limit exceeded
        time.sleep(1)
        data = {'variables': str({"count": '3',
                                  "cursor": cursor,
                                  'id': pageid}),
                'doc_id': docid}
        try:
            resp = requests.post(url='https://www.facebook.com/api/graphql/',
                                 data=data,
                                 headers=headers)
            time.sleep(random.choice([i for i in range(1, 10)]))
            if req_name == 'ProfileCometTimelineFeedRefetchQuery':
                edge_list, cursor, max_date = __parsing_ProfileComet__(resp)
            elif req_name == 'CometModernPageFeedPaginationQuery':
                edge_list, cursor, max_date = __parsing_CometModern__(resp)
            contents = contents + edge_list

            if not has_next_page(resp):
                raise UnboundLocalError(f"Reached the last page")

            # break times to zero
            break_times = 0
        except UnboundLocalError:
            print("Reached the last page")
            break

        except Exception as e:
           # print(f'Break Times {break_times}: [{type(e).__name__}] Exceptions happened with this request. Sleep 15 seconds and retry to request new posts.')
            #print('REQUEST LOG >>  pageid: {}, docid: {}, cursor: {}'.format(pageid, docid, cursor))
           # print('RESPONSE LOG: ', resp.text[:3000])
            #break_times += 1
            print(f'break_times:{break_times}')
            #time.sleep()
            # Get New cookie ID
            headers = __get_cookieid__(pageurl)

            #if break_times > 5:
                #print('break_times:%d，請更換IP！' % break_times)
                #print('Please check your target fanspage has up to date.')
                #print('If so, you can ignore this break time message, if not, please change your Internet IP and retun this crawler.')
    
        except:
            break_times += 1
            print(f'break_times:{break_times}')
    # Join content and requires
    df = pd.DataFrame(contents, columns = ['NAME', 'TIME', 'SELF_LINK', 'MESSAGE', 'POSTID', 'PAGEID', 'COMMENT_COUNT', 'REACTION_COUNT', 'SHARE_COUNT', 'DISPLAYCOMMENTCOUNT', 'REACTIONS', 'CURSOR', 'URL', 'ATTACHMENTS'])

    reaction_type = []
    for reactions in df['REACTIONS']:
        if len(reactions) >= 1:
            for reaction in reactions:
                if reaction['node']['localized_name'] not in reaction_type:
                    reaction_type.append(reaction['node']['localized_name'])
    reaction_type = [reaction.upper() for reaction in reaction_type]
    for reaction in reaction_type:
        df[reaction] = df['REACTIONS'].apply(lambda x: __extract_reactions__(x, reaction))

    df = df.drop('REACTIONS', axis=1)
    df['TIME'] = df['TIME'].apply(lambda x: datetime.datetime.fromtimestamp(int(x)).strftime("%Y-%m-%d %H:%M:%S"))
    df['UPDATETIME'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df
