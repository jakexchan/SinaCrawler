# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class UserBaseItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    u_id = Field()
    u_weibo_count = Field()
    u_following = Field()
    u_fans = Field()
    u_base_info = Field()
    u_experience = Field()
    weibo = Field()


class WeiboItem(Item):
    u_id = Field()
    weibo_content = Field()
    weibo_type = Field()
    weibo_ct = Field()