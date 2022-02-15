# Facebook_Crawler (developed by TIGCR 大數據小組)

## Introduction
* 此Python專案，乃參考TENG-LIN YU(游騰林)的[FB爬蟲套件](https://github.com/TLYu0419/facebook_crawler)，改寫成不須安裝套件的形式。
* 除了爬取Facebook Fanspage、Groups貼文內容及統計資訊以外，再加入從貼文清單中爬取留言的功能 (需設定FB帳號密碼，搭配[chromedriver](https://chromedriver.chromium.org/)一起使用)
* 目前尚不支援爬取貼文的巢狀留言

## Quickstart
### 爬取Fanspage粉專貼文

### 爬取留言
* 使用方法1
-用fb貼文爬蟲的結果取得postid跟pageid，爬取檔案內所有貼文之留言
* 使用方法2
-直接輸入想要爬的貼文postid及pageid(在網址中)，爬取指定貼文留言

* 流程:
1. 取得cookie:
將fb帳號及密碼參數輸入「get_fb_cookie」function

2. 爬取留言:
將 cookie 、postid列表及pageid參數輸入「fb_page_comment_crawler」function

## FAQ
