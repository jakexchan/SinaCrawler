# -*- coding: UTF-8 -*-
from scrapy.selector import Selector

from scrapy.contrib.spiders.init import InitSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.http import Request, FormRequest

from weibo_crawler.items import WeiboCrawlerItem

import time
import re

class WeiboSpider(InitSpider):
	name = 'weibo'
	allowed_domains = ['http://www.weibo.cn']

	keyword = u'北京理工大学珠海学院'
	start_urls = ["http://weibo.cn/search/user/?keyword=" + keyword]

	# rules = (
	# 	Rule(SgmlLinkExtractor(allow = ('/\w+\?f=search\_\d+', )), callback = 'parse_item', follow = True),
	# )

	headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch',
		'Accept-Language': 'en-US,en;q=0.8',
		'Connection': 'keep-alive',
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'
	}


	def start_requests(self):
		return [Request("http://login.weibo.cn/login/", meta = {'cookiejar': 1}, callback = self.login)]

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
			'mobile': '',  #weibo account
			password: '',   #weibo password
			'code': code,
			'remember': 'on',
			'backURL': backURL,
			'backTitle': backTitle,
			'tryCount': tryCount,
			'vk': vk,
			'capId': capId,
			'submit': submit
			}
		else:
			form_data = {
			'mobile': '',  #weibo account
			password: '',   #weibo password
			'remember': 'on',
			'backURL': backURL,
			'backTitle': backTitle,
			'tryCount': tryCount,
			'vk': vk,
			'capId': capId,
			'submit': submit
			}
		print form_data
		print response
		print response.meta['cookiejar']
		return [FormRequest.from_response(response, 
			meta = {'cookiejar': response.meta['cookiejar']},
			headers = self.headers, 
			formdata = form_data, 
			callback = self.after_login, 
			dont_filter = True)]

	def after_login(self, response):
		for url in self.start_urls:
			print 'make requests:' + url
			yield Request(url, meta = {'cookiejar': response.meta['cookiejar']}, headers = self.headers, dont_filter = True)

	def parse(self, response):
		print response
		print response.body
		sel = Selector(response)
		links = sel.xpath('//a[re:test(@href, "/\w+\?f=search\_\d+")]/@href').extract()
		links = list(set(links))
		for link in links:
			new_url = self.allowed_domains[0] + link
			print 'Request new url:'
			print new_url
			yield Request(new_url, meta = {'cookiejar': response.meta['cookiejar']}, headers = self.headers, callback = self.parse_item, dont_filter = True)

	def parse_item(self, response):
		import pdb
		pdb.set_trace()
		item = WeiboCrawlerItem()
		sel = Selector(response)
		ut_element = sel.xpath('//div[@class="ut"]')
		info_link = ut_element.xpath('//a[re:test(@href, "\/\d+\/info")]').extract()[0]
		item['u_id'] = info_link.split('/')[1]
		tip = sel.xpath('//div[@class="tip2"]')[0]
		item['u_weibo_count'] = re.findall('\d+', tip.xpath('//span[@class="tc"]/text()').extract()[0])[0]
		item['u_following'] = re.findall('\d+', tip.xpath('//a[re:test(@href, "\/\d+\/follow")]/text()').extract()[0])[0]
		item['u_fans'] = re.findall('\d+', tip.xpath('//a[re:test(@href, "\/\d+\/fans")]/text()').extract()[0])[0]
		print item
		return item



