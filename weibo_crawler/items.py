# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class WeiboCrawlerItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    u_id = Field()
    u_name = Field()
    u_weibo_count = Field()
    u_following = Field()
    u_fans = Field()
    u_sex = Field()
    u_region = Field()
    u_birthday = Field()
    u_introduction = Field()
    u_tags = Field()
    weibo = Field()
    learn_experience = Field()
    work_experience = Field()