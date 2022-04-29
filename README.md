# Facebook_Crawler (developed by TIGCR 大數據小組)

## Introduction
* 此Python專案，將FB爬蟲功能內容分為三個部分
* 舊版爬蟲程式Crawler.py參考TENG-LIN YU(游騰林)的[FB爬蟲套件](https://github.com/TLYu0419/facebook_crawler)，改寫成不須安裝套件的形式。
* 新版爬蟲程式new_fanpage_post_id_crawler.py，new_fanpage_crawler.py適用於新版Fanpage的爬蟲程式使用Selenium與WebDriver (ChromeDriver)，需自行下載ChromeDriver並置於同一目錄。並確認chromedriver的版本跟你電腦chrome的版本相同
* 爬蟲程式可爬取Facebook Fanspage、Groups貼文內容及統計資訊。
* 留言爬蟲程式(Comment Crawler_v1)可從貼文清單中爬取留言的功能 (需設定FB帳號密碼，搭配[chromedriver](https://chromedriver.chromium.org/)一起使用)

* 由於從FB爬取資料是違反臉書的[使用規則](https://about.fb.com/news/2021/04/how-we-combat-scraping/)，故一但爬取過多的內容，臉書會限制你的IP。目前可參考的一個解決方法是：使用行動網路(e.g.電腦連手機網路)，執行爬蟲，IP被鎖(出現請更換IP的訊息)之後，開啓手機的飛航模式再關掉，IP位子就會換掉了。如果使用的wifi有多個來源，或有2.4G及5G的模組也可以藉由切換不同wifi來切換IP。


## Quickstart
### Crawler.py 
適用於舊版Fanpage的爬蟲程式，此程式不須登入FB帳密
* pageurl：粉絲專頁的網址
* until_date：爬到哪一天結束 (大約的最舊一則貼文日期)

### new_fanpage_post_id_crawler.py 
適用於新版Fanpage的爬蟲程式，取得貼文id
### new_fanpage_crawler.py 
適用於新版Fanpage的爬蟲程式，使用new_fanpage_post_id_crawler.py之後，利用輸出的貼文ID檔案取得貼文內容與互動內容
此兩程式須輸入FB帳密至程式中

### 爬取留言 (fb_page_comments_main.py)
參考[說明.txt](Comment Crawler_v1/說明.txt)

## FAQ
