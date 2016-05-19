# -*- coding: utf-8 -*-
from scrapy.selector import Selector

from scrapy.contrib.spiders.init import InitSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
import os
from scrapy.http import Request, FormRequest
from scrapy.settings import Settings
from weibo_crawler.items import UserBaseItem, WeiboItem
import MySQLdb
import time
import re
import json


class WeiboSpider(InitSpider):
    name = 'weibo'
    allowed_domains = ['http://www.weibo.cn']
    start_urls = ["http://login.weibo.cn/login/"]

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        #'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'
    }

    fp = file(r'/tmp/options.json')
    options =  json.load(fp)
    fp.close

    download_delay = int(options['delay'])
    search_user_url = 'http://weibo.cn/search/user/?keyword='

    keyword = options['keyword']
    begin_page = int(options['begin_page'])
    end_page = int(options['end_page'])

    cook = {"_T_WM": options['t_wm'], 'SUHB': options['suhb'], 'SUB': options['sub'], 'gsid_CTandWM': options['gsid_CTandWM']}


    def start_requests(self):
        return [Request(self.start_urls[0], cookies=self.cook, headers=self.headers, callback=self.after_login, dont_filter=True)]

    def after_login(self, response):
        print u'登录成功'
        url_lists = self.make_url_lists()
        for url in url_lists:
            yield Request(url,
                          cookies=self.cook,
                          headers=self.headers,
                          dont_filter=True)

    def make_url_lists(self):
        url_lists = []
        for i in range(self.begin_page, self.end_page + 1):
            url = self.search_user_url + self.keyword + '&page=' + str(i)
            url_lists.append(url)
        return url_lists

    def parse(self, response):
        sel = Selector(response)
        links = sel.xpath(
            '//a[re:test(@href, "/\w+\?f=search\_\d+")]/@href').extract()
        links = list(set(links))
        for link in links:
            new_url = self.allowed_domains[0] + link
            print '请求用户主页:'
            print new_url
            yield Request(new_url,
                          cookies=self.cook,
                          headers=self.headers,
                          callback=self.parse_item,
                          dont_filter=True)


    def parse_item(self, response):
        item = UserBaseItem()
        sel = Selector(response)

        # 获取用户信息元素
        ut_element = sel.xpath('//div[@class="ut"]')
        info_link = ut_element.xpath(
            '//a[re:test(@href, "\/\d+\/info")]/@href').extract()[0]  # 获取用户信息链接
        u_id = info_link.split('/')[1]

        item['u_id'] = u_id  # 获取微博用户ID号
        tip = sel.xpath('//div[@class="tip2"]')[0]
        item['u_weibo_count'] = re.findall(
            '\d+', tip.xpath('//span[@class="tc"]/text()').extract()[0])[0]  # 获取微博用户发布微博数
        item['u_following'] = re.findall(
            '\d+', tip.xpath('//a[re:test(@href, "\/\d+\/follow")]/text()').extract()[0])[0]  # 获取微博用户关注数
        item['u_fans'] = re.findall(
            '\d+', tip.xpath('//a[re:test(@href, "\/\d+\/fans")]/text()').extract()[0])[0]  # 获取微博用户粉丝数
        weibo_wrap_elements = sel.xpath('//div[@class="c"]')


        for index in range(len(weibo_wrap_elements) - 2):
            weibo_item = WeiboItem()
            weibo_item['u_id'] = u_id
            weibo_item['weibo_content'] = weibo_wrap_elements[
                index].xpath('.//span[@class="ctt"]/text()').extract()[0]  # 获取发布微博内容
            weibo_item['weibo_ct'] = weibo_wrap_elements[
                index].xpath('.//span[@class="ct"]/text()').extract()
            subnode_count = len(weibo_wrap_elements[index].xpath('.//div'))
            if subnode_count > 2:
                weibo_item['weibo_type'] = u'转发'
            else:
                weibo_item['weibo_type'] = u'原创'
            yield weibo_item


        # Make the user info url
        info_url = "http://weibo.cn" + info_link
        print '发送请求资料URL:'
        print info_url
        yield Request(info_url,
                      cookies=self.cook,
                      meta={'item': item},
                      headers=self.headers,
                      callback=self.parse_info,
                      dont_filter=True)


    def parse_info(self, response):
        item = response.meta['item']
        sel = Selector(response)
        item['u_base_info'] = sel.xpath(
            "//div[@class='c'][3]//text()").extract()
        item['u_experience'] = sel.xpath(
            "//div[@class='c'][4]//text()").extract()
        return item
