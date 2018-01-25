# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ZhiLianItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    min_salary = Field()
    max_salary = Field()
    job_area = Field()
    date = Field()
    job_people = Field()
    jin_yan = Field()
    xue_li = Field()
    job_num = Field()
    lei_bie = Field()
    what_todo = Field()
    what_command = Field()
    work_duty_content = Field()
    work_info_url = Field()
    company_name = Field()
    company_xin_zhi = Field()
    company_num = Field()
    company_url = Field()
    what_work = Field()
    company_place = Field()
    company_introduce = Field()
