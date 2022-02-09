import fb_crawler as fb
## 範例一：爬取粉絲專頁  fb.Crawl_PagePosts()
## 參數說明：
#   1. pageurl：粉絲專頁的網址
#   2. until_date：爬到哪一天為止

pageurl= 'https://www.facebook.com/mohw.gov.tw'
df_pages = fb.Crawl_PagePosts(pageurl=pageurl, until_date='2021-07-05')
df_pages.to_csv('衛生福利部.csv',index=False,encoding='utf-8-sig')

