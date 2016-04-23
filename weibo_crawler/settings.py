# -*- coding: utf-8 -*-

# Scrapy settings for weibo_crawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'weibo_crawler'

SPIDER_MODULES = ['weibo_crawler.spiders']
NEWSPIDER_MODULE = 'weibo_crawler.spiders'

COOKIES_ENABLED = True
#COOKIES_DEBUG = True

DOWNLOAD_DELAY = 10
DOWNLOAD_TIMEOUT = 30

DOWNLOADER_MIDDLEWARES = {
        'weibo_crawler.comm.rotate_useragent.RotateUserAgentMiddleware' :400
    }
# Crawl responsibly by identifying yourself (and your website) on the

ITEM_PIPELINES = {
    'weibo_crawler.pipelines.JsonWriterPipeline': 300,
    'weibo_crawler.pipelines.WeiboCrawlerPipeline': 300,
}

# MySQL database configure setting
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_DBNAME = 'testDB'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
