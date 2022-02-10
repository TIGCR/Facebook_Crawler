import fb_crawler as fb
import time
  # import facebook_crawler as fb
'''
參數說明：
1. pageurl：粉絲專頁的網址
2. until_date：爬到哪一天為止
'''
start = time.time()

pageurl= 'https://www.facebook.com/mohw.gov.tw'
df_pages = fb.Crawl_PagePosts(pageurl=pageurl, until_date='2022-02-01')

end = time.time()
print("Running Time:%.2f" % (end-start))

df_pages.to_csv('粉專貼文.csv',index=False,encoding='utf-8-sig')



