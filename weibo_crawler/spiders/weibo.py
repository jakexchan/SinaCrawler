# -*- coding: UTF-8 -*-
from scrapy.selector import Selector

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from scrapy.http import Request, FormRequest

from weibo_crawler.items import WeiboCrawlerItem

class WeiboSpider(CrawlSpider):
	name = 'weibo'
	allowed_domains = ['weibo.cn']

	keyword = u'北京理工大学珠海学院'
	start_urls = ["http://weibo.cn/search/user/?keyword=" + keyword]

	rules = (
		Rule(SgmlLinkExtractor(allow = ('/\w+\?f=search\_\d+', )), callback = 'parse_item'),
	)

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
			yield Request(url, meta = {'cookiejar': response.meta['cookiejar']}, headers = self.headers, callback = self.parse_page, dont_filter = True)

	def parse_page(self, response):
		print response
		print response.body
		html = Selector(response)
		print html

	def parse_item(self, response):
		pass
		

		


