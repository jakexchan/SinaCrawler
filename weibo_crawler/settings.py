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
COOKIES_DEBUG = True

DOWNLOAD_DELAY = 15
DOWNLOAD_TIMEOUT = 30

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'
