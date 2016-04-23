# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
from scrapy import log
from twisted.enterprise import adbapi

from weibo_crawler.items import UserBaseItem, WeiboItem

import json
import codecs
import time, datetime
import re

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
        fp = file(r'/tmp/options.json')
        options =  json.load(fp)
        fp.close
        self.user_table_name = options['user_table_name']
        self.weibo_table_name = options['weibo_table_name']
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            port=settings['MYSQL_PORT'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            cursorclass=MySQLdb.cursors.DictCursor,
            charset='utf8',
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        if isinstance(item, UserBaseItem):
            query = self.dbpool.runInteraction(self._user_insert, item, spider)
        if isinstance(item, WeiboItem):
            query = self.dbpool.runInteraction(self._weibo_insert, item, spider)
        query.addErrback(self._handle_error, item, spider)
        query.addBoth(lambda _: item)
        return query

    def _user_insert(self, conn, item, spider):
        
        
        school = self.get_school_value(item['u_experience'])

        name,sex, region, birthday, introduction, tags = self.get_user_info(item['u_base_info'])

        conn.execute("""
            insert into """ + self.user_table_name + """(u_id, u_name, u_weibo_count, u_following, u_fans, u_sex, u_region, u_birthday, u_introduction, u_tags ,u_school)
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (item['u_id'], name, int(item['u_weibo_count']), int(item['u_following']), int(item['u_fans']), sex, region, birthday, introduction, tags, school))
    
    def _weibo_insert(self, conn, item, spider):
        #\xc2\xa0\xe6\x9d\xa5\xe8\x87\xaa
        day, time, client = self.deal_weibo_ct(item['weibo_ct'][0])
        conn.execute("""
            insert into """ + self.weibo_table_name +"""(u_id, w_content, w_type, w_day, w_time, w_client)
            values(%s, %s, %s, %s, %s, %s)
        """, (item['u_id'], item['weibo_content'], item['weibo_type'], day, time, client))

    def _handle_error(self, failue, item, spider):
        log.err(failue)

    def deal_weibo_ct(self, ct_str):
        global time
        ct_str = re.sub(r'[\xa0]', " ", ct_str)  #remove &nbsp;
        ct_str = ct_str.replace(u'来自', '')  #remove

        if ct_str.find(u'年') >= 0:
            ct_str = ct_str.replace(u'年', '-').replace(u'月', '-').replace(u'日', '')
        elif ct_str.find(u'月') >= 0:
            year = datetime.datetime.now().year
            ct_str = ct_str.replace(u'月', '-').replace(u'日', '')
            ct_str = str(year) + '-' + ct_str
        
        arr = ct_str.split(' ')
        
        day, time,client = None, None, None

        for index,item in enumerate(arr):
            if index == 0:
                day = item
            elif index == 1:
                time = item
            elif index == 2:
                client = item

        if day == u'今天':
            day = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        return day, time, client


    def get_school_value(self, u_school_item):
        result = ''
        for index in u_school_item:
            result += index + u';'
        return result

    def get_user_info(self, info_item):
        name,sex, region, birthday, introduction, tags = None, None, None, None, None, ''
        tag_index = None
        for index, item in enumerate(info_item):
            if item == '':
                continue
            if item.find(u"昵称") >= 0:
                name = item.split(':')[1]
            elif item.find(u'性别') >= 0:
                sex = item.split(':')[1]
            elif item.find(u'地区') >= 0:
                region = item.split(':')[1]
            elif item.find(u'生日') >= 0:
                birthday = item.split(':')[1]
            elif item.find(u'简介') >= 0:
                introduction = item.split(':')[1]
            elif item.find(u'标签') >= 0:
                tag_index = index

        i = tag_index - len(info_item) + 1
        for index in info_item[i:-1]:
            if index == '':
                continue
            else:
                tags += index
        return name, sex, region, birthday, introduction, tags


