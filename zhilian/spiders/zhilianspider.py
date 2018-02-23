# -*- coding:utf-8 -*-

# Python内置库
import re
import time
from urllib import parse

# 第三方库
import scrapy
from scrapy.spiders import Spider
from lxml import etree

# 项目内部库
from zhilian.utils import utils
from zhilian.items import ZhiLianItem
from zhilian.utils import select_data


class ZhiLianSpider(Spider):
    name = "zhi_lian"
    key = parse.quote("大数据")
    url = "http://sou.zhaopin.com/jobs/searchresult.ashx?jl={}&kw={}&p={}&isadv=0"

    def start_requests(self):
        area_data = select_data.parse()
        for i in area_data:
            a = i['area']
            area = parse.quote(a)
            start_urls = self.url.format(area, self.key, 1)
            yield scrapy.Request(url=start_urls, callback=self.parse, meta={'area': area})

    def parse(self, response):
        page_num = self.get_page_num(response)
        area = response.meta['area']
        for pn in range(1, int(page_num)):
            start_urls = self.url.format(area, self.key, pn)
            yield scrapy.Request(url=start_urls, callback=self.parse0)

    def parse0(self, response):
        html = response.body
        selector = etree.HTML(html)
        url = selector.xpath('//td[@class="zwmc"]/div/a/@href')
        for i in url:
            yield scrapy.Request(url=i, callback=self.get_job_info, meta={'url': i})

    @staticmethod
    def get_page_num(response):
        selector = etree.HTML(response.body)
        page = selector.xpath('//span[@class="search_yx_tj"]/em/text()')[0]
        if re.search('(\d+)+\.+(\d+)', str(float(page) / 60)):
            if int(re.findall('(\d+)+\.', str(float(page) / 60))[0]) + 1 >= 90:
                page_num = 90
            else:
                page_num = int(re.findall('(\d+)+\.', str(float(page) / 60))[0]) + 1
        else:
            if int(page) / 60 >= 90:
                page_num = 90
            else:
                page_num = int(page) / 60
        return page_num

    def get_job_info(self, response):
        item = ZhiLianItem()
        selector = etree.HTML(response.body)
        url = response.meta['url']
        wenben = []
        if selector.xpath('//div[@class="terminalpage-left"]'):
            # 获取招聘信息主要内容
            money = selector.xpath(
                '//div[@class="terminalpage-left"]'
                '/ul[@class="terminal-ul clearfix"]'
                '/li[1]/strong/text()')[0].replace("元/月", "").split("-")
            d = selector.xpath(
                '//div[@class="terminalpage-left"]'
                '/ul[@class="terminal-ul clearfix"]'
                '/li[3]/strong/span/text()|'
                '//div[@class="terminalpage-left"]'
                '/ul[@class="terminal-ul clearfix"]'
                '/li[3]/strong/span/text()')[0]
            job_people = selector.xpath(
                '//div[@class="terminalpage-left"]'
                '/ul[@class="terminal-ul clearfix"]'
                '/li[4]/strong/text()')[0]
            jin_yan = selector.xpath(
                '//div[@class="terminalpage-left"]'
                '/ul[@class="terminal-ul clearfix"]'
                '/li[5]/strong/text()')[0]
            xue_li = selector.xpath(
                '//div[@class="terminalpage-left"]'
                '/ul[@class="terminal-ul clearfix"]'
                '/li[6]/strong/text()')[0]
            job_num = selector.xpath(
                '//div[@class="terminalpage-left"]'
                '/ul[@class="terminal-ul clearfix"]'
                '/li[7]/strong/text()')[0]
            lei_bie = selector.xpath(
                '//div[@class="terminalpage-left"]'
                '/ul[@class="terminal-ul clearfix"]'
                '/li[8]/strong/a/text()')[0]
            jobplace = selector.xpath(
                'string(//div[@class="terminalpage-left"]'
                '/ul[@class="terminal-ul clearfix"]'
                '/li[2]/strong/a)')
            command = selector.xpath(
                'string(//div[@class="tab-inner-cont"])').strip().replace('查看工作地图', '')
            wenben.append(command)
            h = re.sub('\r\n\s+', '', wenben[0])
            if re.findall('岗位职责(.*?)岗位要求', str(h)):
                try:
                    what_todo = re.findall(
                        '岗位职责(.*?)岗位要求',
                        str(h))[0].replace(
                        ':',
                        '').replace(
                        '：',
                        '')
                    what_command = re.findall(
                        '岗位要求(.*?)工作地址',
                        str(h))[0].replace(
                        ':',
                        '').replace(
                        '：',
                        '')
                    work_duty_content = ''
                except Exception as err:
                    print(err)
                    what_todo = ''
                    what_command = ''
                    work_duty_content = h[0:500]
            elif re.findall('岗位职责(.*?)任职', str(h)):
                try:
                    what_todo = re.findall(
                        '岗位职责(.*?)任职',
                        str(h))[0].replace(
                        ':',
                        '').replace(
                        '：',
                        '')
                    what_command = re.findall(
                        '要求(.*?)工作地址',
                        str(h))[0].replace(
                        ':',
                        '').replace(
                        '：',
                        '')
                    work_duty_content = ''
                except Exception as err:
                    print(err)
                    what_todo = ''
                    what_command = ''
                    work_duty_content = h[0:500]
            else:
                what_todo = ''
                what_command = ''
                work_duty_content = h[0:500]
                pass
            if re.findall('工作地址：(\w+)', str(h)):
                totalplace = re.findall('工作地址：(\w+)', str(h))
            else:
                totalplace = ''
            if totalplace[0] != '':
                jobarea = jobplace + '-' + totalplace[0]
            else:
                jobarea = jobplace
            try:
                floatdate = time.mktime(time.strptime(d, '%Y-%m-%d %H:%M:%S'))*1000
                date = re.findall('(\d+)+\.', str(floatdate))[0]
            except Exception as err:
                print(err)
                date = '最近or招聘中'
            if len(money) == 2:
                min_salary = utils.change_to_k(int(money[0]))
                max_salary = utils.change_to_k(int(money[1]))
                item['min_salary'] = min_salary
                item['max_salary'] = max_salary
            else:
                item['min_salary'] = money[0]
                item['max_salary'] = money[0]
            item['from_website'] = '智联'
            item['location'] = jobarea
            item['publish_date'] = date
            item['work_type'] = job_people
            item['work_experience'] = jin_yan
            item['limit_degree'] = xue_li
            item['people_count'] = job_num
            item['career_type'] = lei_bie
            item['work_duty'] = what_todo
            item['work_need'] = what_command
            item['work_duty_content'] = work_duty_content
            item['work_info_url'] = url
            company_url = selector.xpath('//div[@class="fixed-inner-box"]/div[1]/h2/a/@href')[0]
            print(company_url)
            yield scrapy.Request(company_url,
                                 callback=self.get_company_info,
                                 headers={'referer': company_url},
                                 meta={'item': item, 'front_html': selector})

    @staticmethod
    def get_company_info(response):
        selector = etree.HTML(response.body)
        item = response.meta['item']
        if selector.xpath('//div[@class="mainLeft"]'):
            company_name = selector.xpath(
                '//div[@class="mainLeft"]'
                '/div[1]/h1/text()')[0].strip()
            company_xin_zhi = selector.xpath(
                '//div[@class="mainLeft"]'
                '/div[1]/table/tr[1]/td[2]/span/text()')[0]
            company_num = selector.xpath(
                '//div[@class="mainLeft"]'
                '/div[1]/table/tr[2]/td[2]/span/text()')[0]
            company_introduce = selector.xpath(
                'string(//div[@class="company-content"])').strip()
            if selector.xpath('//div[@class="mainLeft"]/div[1]/table/tr[3]/td[2]/span/a'):
                company_url = selector.xpath(
                    '//div[@class="mainLeft"]'
                    '/div[1]/table/tr[3]/td[2]/span/a/@href')[0]
                what_work = selector.xpath(
                    '//div[@class="mainLeft"]'
                    '/div[1]/table/tr[4]/td[2]/span/text()')[0]
                try:
                    company_location = selector.xpath(
                        '//div[@class="mainLeft"]'
                        '/div[1]/table/tr[5]/td[2]/span/text()')[0]
                except Exception as err:
                    print(err)
                    company_location = ''
            else:
                company_url = ''
                what_work = selector.xpath(
                    '//div[@class="mainLeft"]'
                    '/div[1]/table/tr[3]/td[2]/span/text()')[0]
                try:
                    company_location = selector.xpath(
                        '//div[@class="mainLeft"]'
                        '/div[1]/table/tr[4]/td[2]/span/text()')[0]
                except Exception as err:
                    print(err)
                    company_location = ''
            item['business_website'] = company_url
            item['business_industry'] = what_work
            item['business_location'] = company_location
            item['business_name'] = company_name
            item['business_type'] = company_xin_zhi
            item['business_count'] = company_num
            item['business_info'] = company_introduce
            print(item)
            yield item
        else:
            front_html = response.meta['front_html']
            c_info = []
            if front_html.xpath(
                    'string(//ul[@class="terminal-ul clearfix terminal-company mt20"])'):
                front_html = front_html.xpath(
                    'string(//ul[@class="terminal-ul clearfix terminal-company mt20"])').strip()
                c_info.append(front_html)
                a = re.sub('\r\n\s+', '', c_info[0]).replace('/', '')
                h = re.sub('\s+', '', a)
                company_name = front_html.xpath('string(//p[@class="company-name-t"]/a)')
                company_xin_zhi = re.findall('公司性质：(\w+)公司', str(h))[0]
                company_num = re.findall('公司规模：(.*?)公司', str(h))[0]
                what_work = re.findall('公司行业：(\w+)公司', str(h))[0]
                company_place = re.findall('公司地址：(\w+)', str(h))[0]
                try:
                    company_url = re.findall('公司主页：(.*?)公司', str(h))[0]
                    item['business_website'] = company_url
                except Exception as err:
                    print(err)
                    item['business_website'] = ""
                    pass
                company_introduce = ""
                item['business_name'] = company_name
                item['business_type'] = company_xin_zhi
                item['business_count'] = company_num
                item['business_industry'] = what_work
                item['business_location'] = company_place
                item['business_info'] = company_introduce
                yield item
