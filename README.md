# Facebook_Crawler (developed by TIGCR 大數據小組)

## Introduction
* 此Python專案，主要為實現從FB爬取貼文、留言等功能。我們實作了Selenium及Web Driver爬取FB貼文ID的功能(Fanspage、Groups貼文內容及統計資訊)，但由於FB MBASIC改版，目前該程式無法正確抓取貼文的相關留言數、共享數統計。
* 目前可用的爬蟲程式Crawler.py import了參考TENG-LIN YU(游騰林)的[FB爬蟲套件](https://github.com/TLYu0419/facebook_crawler)的程式，改寫成不須安裝套件的形式。
* 由於從FB爬取資料是違反臉書的[使用規則](https://about.fb.com/news/2021/04/how-we-combat-scraping/)，故一但爬取過多的內容，臉書會限制你的IP。目前可參考的一個解決方法是：使用行動網路(e.g.電腦連手機網路)，執行爬蟲，IP被鎖(出現請更換IP的訊息)之後，開啓手機的飛航模式再關掉，IP位子就會換掉了。如果使用的wifi有多個來源，或有2.4G及5G的模組也可以藉由切換不同wifi來切換IP。我們修改的程式增加了爬取的間隔以增加穩定度，且當ip被封鎖時，改成讓程式持續運行，並可手動更改ip讓程式繼續。

* 留言爬蟲程式(Comment Crawler_v1)可從貼文清單中爬取留言的功能 (需設定FB帳號密碼，搭配[chromedriver](https://chromedriver.chromium.org/)一起使用)


## Quickstart
### Crawler.py 
* pageurl：粉絲專頁的網址
* until_date：爬到哪一天結束 (大約的最舊一則貼文日期)

### new_fanpage_post_id_crawler.py (不再更新)
適用於新版Fanpage的爬蟲程式，取得貼文id
### new_fanpage_crawler.py (已無法取得部分貼文部分資訊、不再更新)
適用於新版Fanpage的爬蟲程式，使用new_fanpage_post_id_crawler.py之後，利用輸出的貼文ID檔案取得貼文內容與互動內容 (貼文內容僅能取得部份)。此兩程式須輸入FB帳密至程式中

### 爬取留言 (fb_page_comments_main.py)
參考[說明.txt](https://github.com/TIGCR/Facebook_Crawler/blob/main/Comment%20Crawler_v1/%E8%AA%AA%E6%98%8E.txt)

## FAQ
