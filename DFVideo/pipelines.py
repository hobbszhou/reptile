# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
from scrapy.exceptions import DropItem
import os
import sys
class DfvideoPipeline(object):
    def open_spider(self, spider):
        self.conn = pymysql.connect(
            host='',
            port=3306,
            db='lottery',
            user='root',
            password='',
            charset='utf8mb4',
        )
        self.cur = self.conn.cursor()
    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
    def process_item(self, item, spider):
        # keys = item.keys()
        # values = [item[k] for k in keys]
        keys, values = zip(*item.items())
        print(keys, " ========= ",  item.table_name)
        sql = "insert into `{}` ({}) values ({}) " \
              "ON DUPLICATE KEY UPDATE {}".format(
            item.table_name,
            ','.join(keys),
            ','.join(['%s'] * len(values)),
            ','.join(['`{}`=%s'.format(k) for k in keys])
        )
        self.cur.execute(sql, values * 2)
        self.conn.commit()
        print(self.cur._last_executed)


        return item