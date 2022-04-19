import pandas as pd
import fb_page_comments_crawler as fb

#讀取fb密碼
# with open('PW.txt') as f:
#     pw = f.readlines()
#     f.close()

#取得登入cookie
# s = fb.get_fb_cookie(pw[0], pw[1])  
s = fb.get_fb_cookie('your id', 'your password')

#讀取postid資料
ndf = pd.read_csv('粉專貼文.csv (從crawler.py取得)')
pageid = str(ndf.PAGEID.unique()[0])
postid_list = [str(i) for i in ndf.POSTID]

#開始爬取
fb.fb_page_comment_crawler(s, postid_list[:2], pageid)

# test.to_csv("柯文哲貼文留言_測試1.csv", encoding = 'utf-8-sig')