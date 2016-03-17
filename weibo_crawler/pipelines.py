# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
from scrapy import log
from twisted.enterprise import adbapi

from weibo_crawler.items import WeiboCrawlerItem

import json
import codecs

import MySQLdb
import MySQLdb.cursors


class JsonWriterPipeline(object):
    """docstring for JsonWriterPipeline"""

    def __init__(self):
        self.file = codecs.open('weibo.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()


class WeiboCrawlerPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            port=settings['MYSQL_PORT'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf-8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._user_insert, item, spider)
        query = self.dbpool.runInteraction(self._weibo_insert, item, spider)
        query.addErrback(self._handle_error, item, spider)
        query.addBoth(lambda _: item)
        return query

    def _user_insert(self, conn, item, spider):
        pass

    def _weibo_insert(self, conn, item, spider):
        pass

    def _handle_error(self, failue, item, spider):
        log.err(failue)
