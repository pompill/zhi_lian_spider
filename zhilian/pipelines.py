# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.conf import settings


class ZhilianPipeline(object):
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        self.client.admin.authenticate(settings['MONGO_USER'], settings['MONGO_PSW'])
        self.zhilian = self.client[settings['MONGO_DB']]
        self.zhilianData = self.zhilian[settings['MONGO_COLL']]
        pass

    def process_item(self, item, spider):
        data = {
            'from_website': item['from_website'],
            'min_salary': item['min_salary'],
            'max_salary': item['max_salary'],
            'location': item['job_area'],
            'publish_date': item['date'],
            'work_type': item['job_people'],
            'work_experience': item['jin_yan'],
            'limit_degree': item['xue_li'],
            'people_count': item['job_num'],
            'career_type': item['lei_bie'],
            'work_duty': item['what_todo'],
            'work_need': item['what_command'],
            'work_duty_content': item['work_duty_content'],
            'work_info_url': item['work_info_url'],
            'business_name': item['company_name'],
            'business_type': item['company_xin_zhi'],
            'business_count': item['company_num'],
            'business_website': item['company_url'],
            'business_industry': item['what_work'],
            'business_location': item['company_place'],
            'business_info': item['company_introduce'],
        }
        self.zhilianData.insert_one(data)
        return item

    def close_spider(self, spider):
        pass
