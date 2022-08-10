import pandas as pd
import comment_crawler as fb

#讀取fb密碼
# with open('PW.txt') as f:
#     pw = f.readlines()
#     f.close()

#取得登入cookie
email='your id'
password='your password'
s = fb.get_fb_cookie(email, password)

#讀取postid資料
ndf = pd.read_csv('粉專貼文.csv')
pageid = str(ndf.PAGEID.unique()[0])
postid_list = [str(i) for i in ndf.POSTID]



#開始爬取
df=fb.fb_page_comment_crawler(s, postid_list[:3], pageid)
df=pd.concat(df).reset_index(drop=True)
df.to_excel('留言.xlsx')
