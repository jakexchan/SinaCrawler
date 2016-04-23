# -*- coding: utf-8 -*-
from scrapy.selector import Selector

from scrapy.contrib.spiders.init import InitSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.http import Request, FormRequest

from weibo_crawler.items import UserBaseItem, WeiboItem

import time
import re
import json

class WeiboSpider(InitSpider):
    name = 'weibo'
    allowed_domains = ['http://www.weibo.cn']
    keyword = u'北京理工大学珠海学院'
    pages = 1
    start_urls = ["http://login.weibo.cn/login/"]

    search_user_url = u"http://weibo.cn/search/user/?keyword="

    # rules = (
    #     Rule(SgmlLinkExtractor(allow = (r'/\w+\?f=search\_\d+',)), callback = 'parse_item', follow = True),
    # )

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        #'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'
    }

    def start_requests(self):
        return [Request(self.start_urls[0], meta={'cookiejar': 1}, callback=self.login)]

    def login(self, response):
        sel = Selector(response)
        backURL = sel.xpath("//input[@name='backURL']/@value").extract()[0]
        vk = sel.xpath("//input[@name='vk']/@value").extract()[0]
        capId = sel.xpath("//input[@name='capId']/@value").extract()[0]
        backTitle = sel.xpath("//input[@name='backTitle']/@value").extract()[0]
        tryCount = sel.xpath("//input[@name='tryCount']/@value").extract()[0]
        submit = sel.xpath("//input[@name='submit']/@value").extract()[0]

        password = sel.xpath("//input[@type='password']/@name").extract()[0]

        if sel.xpath("//img/@alt").extract()[0] == u'请打开图片显示':
            imgURL = sel.xpath("//img/@src").extract()[0]
            print '验证码地址:'
            print imgURL
            print '请输入验证码:'
            code = raw_input()
            form_data = {
                'mobile': '',  # weibo account
                password: '',  # weibo password
                'code': code,
                'remember': 'on',
                'backURL': backURL,
                'backTitle': backTitle,
                'tryCount': tryCount,
                'vk': vk,
                'capId': capId,
                'submit': submit
            }
        return [FormRequest.from_response(response,
                                          meta={'cookiejar': response.meta[
                                              'cookiejar']},
                                          headers=self.headers,
                                          formdata=form_data,
                                          callback=self.after_login,
                                          dont_filter=True)]

    def after_login(self, response):
        print u'登录成功'
        url_lists = self.make_url_lists()
        for url in url_lists:
            time.sleep(3)
            yield Request(url,
                          meta={'cookiejar': response.meta['cookiejar']},
                          headers=self.headers,
                          dont_filter=True)

    def make_url_lists(self):
        url_lists = []
        for i in range(1, self.pages + 1):
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
                          meta={'cookiejar': response.meta['cookiejar']},
                          headers=self.headers,
                          callback=self.parse_item,
                          dont_filter=True)

    def parse_item(self, response):
        item = UserBaseItem()
        sel = Selector(response)

        # Get the user info wrap element
        ut_element = sel.xpath('//div[@class="ut"]')
        info_link = ut_element.xpath(
            '//a[re:test(@href, "\/\d+\/info")]/@href').extract()[0]  # Get the user info link
        u_id = info_link.split('/')[1]
        item['u_id'] = u_id  # Get the user id

        tip = sel.xpath('//div[@class="tip2"]')[0]
        item['u_weibo_count'] = re.findall(
            '\d+', tip.xpath('//span[@class="tc"]/text()').extract()[0])[0]  # Get the user weibo counts
        item['u_following'] = re.findall(
            '\d+', tip.xpath('//a[re:test(@href, "\/\d+\/follow")]/text()').extract()[0])[0]  # Get the user following counts
        item['u_fans'] = re.findall(
            '\d+', tip.xpath('//a[re:test(@href, "\/\d+\/fans")]/text()').extract()[0])[0]  # Get the user fans counts

        weibo_wrap_elements = sel.xpath('//div[@class="c"]')

        #weibo_items = []
        for index in range(len(weibo_wrap_elements)-2):
            weibo_item = WeiboItem()
            weibo_item['u_id'] = u_id
            weibo_item['weibo_content'] = weibo_wrap_elements[index].xpath('.//span[@class="ctt"]/text()').extract()[0]
            weibo_item['weibo_ct'] = weibo_wrap_elements[index].xpath('.//span[@class="ct"]/text()').extract()
            subnode_count = len(weibo_wrap_elements[index].xpath('.//div'))
            if subnode_count > 2:
                weibo_item['weibo_type'] = u'转发'
            else:
                weibo_item['weibo_type'] = u'原创'
            yield weibo_item
            #weibo_items.append(json.dumps(weibo_item))
        #item['weibo'] = weibo_items

        # Make the user info url
        info_url = "http://weibo.cn" + info_link
        print '发送请求资料URL:'
        print info_url
        yield Request(info_url,
                      meta={'cookiejar': response.meta['cookiejar'], 'item': item},
                      headers=self.headers,
                      callback=self.parse_info,
                      dont_filter=True)

    def parse_info(self, response):
        item = response.meta['item']
        sel = Selector(response)
        item['u_base_info'] = sel.xpath("//div[@class='c'][3]//text()").extract()
        item['u_experience'] = sel.xpath("//div[@class='c'][4]//text()").extract()
        return item