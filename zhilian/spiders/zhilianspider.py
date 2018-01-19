# -*- coding:utf-8 -*-
from scrapy.spiders import Spider
import scrapy
from zhilian.items import ZhiLianItem
from lxml import etree
import re
import redis
from urllib import parse
import time
from zhilian import changeK


class ZhiLianSpider(Spider):
    name = "zhi_lian"
    r = redis.Redis(host='localhost', port=6379, db=0)
    key = parse.quote("大数据")
    # start_urls = ['http://sou.zhaopin.com/jobs/searchresult.ashx?bj=4010200&sj=2153&in=210500&jl=%E5%B9%BF%E5%B7%9E&p=1&isadv=0']
    url = "http://sou.zhaopin.com/jobs/searchresult.ashx?jl={}&kw={}&p={}&isadv=0"

    def start_requests(self):
        while True:
            area = parse.quote(self.r.spop('area'))
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
            money = selector.xpath('//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[1]/strong/text()')[0].replace("元/月","").split("-")
            d = selector.xpath('//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[3]/strong/span/text()|//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[3]/strong/span/text()')[0]
            jobpeople = selector.xpath('//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[4]/strong/text()')[0]
            jingyan = selector.xpath('//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[5]/strong/text()')[0]
            xueli = selector.xpath('//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[6]/strong/text()')[0]
            jobnum = selector.xpath('//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[7]/strong/text()')[0]
            leibie = selector.xpath('//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[8]/strong/a/text()')[0]
            jobplace = selector.xpath('//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[2]/strong/a/text()')
            command = selector.xpath('string(//div[@class="tab-inner-cont"])').strip()
            wenben.append(command)
            h = re.sub('\r\n\s+', '', wenben[0])
            if re.findall('岗位职责(.*?)岗位要求', str(h)):
                try:
                    whattodo = re.findall('岗位职责(.*?)岗位要求', str(h))[0].replace(':','').replace('：','')
                    whatcommand = re.findall('岗位要求(.*?)工作地址', str(h))[0].replace(':','').replace('：','')
                    work_duty_content = ''
                except:
                    whattodo = ''
                    whatcommand = ''
                    work_duty_content = h[0:500]
            elif re.findall('岗位职责(.*?)任职', str(h)):
                try:
                    whattodo = re.findall('岗位职责(.*?)任职', str(h))[0].replace(':','').replace('：','')
                    whatcommand = re.findall('要求(.*?)工作地址', str(h))[0].replace(':','').replace('：','')
                    work_duty_content = ''
                except:
                    whattodo = ''
                    whatcommand = ''
                    work_duty_content = h[0:500]
            else:
                whattodo = ''
                whatcommand = ''
                work_duty_content = h[0:500]
                pass
            if re.findall('工作地址：(\w+)', str(h)):
                totalplace = re.findall('工作地址：(\w+)', str(h))
            else:
                totalplace = ''
            if totalplace[0] != '':
                jobarea = jobplace[0] + totalplace[0]
            else:
                jobarea = jobplace[0]
            try:
                floatdate = time.mktime(time.strptime(d, '%Y-%m-%d %H:%M:%S'))*1000
                date = re.findall('(\d+)+\.',str(floatdate))[0]
            except:
                date = '最近or招聘中'
            if len(money) == 2:
                min_salary = changeK.change_to_k(int(money[0]))
                max_salary = changeK.change_to_k(int(money[1]))
                item['min_salary'] = min_salary
                item['max_salary'] = max_salary
            else:
                item['min_salary'] = money[0]
                item['max_salary'] = money[0]
            # oba[0]if re.findall(r'</a>"-(.*?)</strong></li>',str(response.body)):
            #     jobarea = joba[0] + re.findall(r'</a>-(.*?)</strong></li>',str(response.body))
            # else:
            #     jobarea = j
            item['job_area'] = jobarea[:-6]
            item['date'] = date
            item['job_people'] = jobpeople
            item['jin_yan'] = jingyan
            item['xue_li'] = xueli
            item['job_num'] = jobnum
            item['lei_bie'] = leibie
            item['what_todo'] = whattodo
            item['what_command'] = whatcommand
            item['work_duty_content'] = work_duty_content
            item['work_info_url'] = url
            companyurl = selector.xpath('//div[@class="fixed-inner-box"]/div[1]/h2/a/@href')[0]
            print(companyurl)
            yield scrapy.Request(companyurl, callback=self.get_company_info, headers={'referer':companyurl}, meta={'item': item, 'front_html': selector})

    def get_company_info(self, response):
        selector = etree.HTML(response.body)
        item = response.meta['item']
        if selector.xpath('//div[@class="mainLeft"]'):
            companyname = selector.xpath('//div[@class="mainLeft"]/div[1]/h1/text()')[0].strip()
            compyxingzhi = selector.xpath('//div[@class="mainLeft"]/div[1]/table/tr[1]/td[2]/span/text()')[0]
            compynum = selector.xpath('//div[@class="mainLeft"]/div[1]/table/tr[2]/td[2]/span/text()')[0]
            compyintroduce = selector.xpath('string(//div[@class="company-content"])').strip()
            if selector.xpath('//div[@class="mainLeft"]/div[1]/table/tr[3]/td[2]/span/a'):
                compyurl = selector.xpath('//div[@class="mainLeft"]/div[1]/table/tr[3]/td[2]/span/a/@href')[0]
                whatwork = selector.xpath('//div[@class="mainLeft"]/div[1]/table/tr[4]/td[2]/span/text()')[0]
                try:
                    compyplace = selector.xpath('//div[@class="mainLeft"]/div[1]/table/tr[5]/td[2]/span/text()')[0]
                except:
                    compyplace = ''
            else:
                compyurl = ''
                whatwork = selector.xpath('//div[@class="mainLeft"]/div[1]/table/tr[3]/td[2]/span/text()')[0]
                try:
                    compyplace = selector.xpath('//div[@class="mainLeft"]/div[1]/table/tr[4]/td[2]/span/text()')[0]
                except:
                    compyplace = ''
            item['company_url'] = compyurl
            item['what_work'] = whatwork
            item['company_place'] = compyplace
            item['company_name'] = companyname
            item['company_xin_zhi'] = compyxingzhi
            item['company_num'] = compynum
            item['company_introduce'] = compyintroduce
            print(item)
            yield item
        else:
            front_html = response.meta['front_html']
            c_info = []
            if front_html.xpath('string(//ul[@class="terminal-ul clearfix terminal-company mt20"])'):
                all = front_html.xpath('string(//ul[@class="terminal-ul clearfix terminal-company mt20"])').strip()
                c_info.append(all)
                a = re.sub('\r\n\s+', '', c_info[0]).replace('/', '')
                h = re.sub('\s+', '', a)
                companyname = front_html.xpath('string(//p[@class="company-name-t"]/a)')
                compyxingzhi = re.findall('公司性质：(\w+)公司', str(h))[0]
                compynum = re.findall('公司规模：(.*?)公司', str(h))[0]
                whatwork = re.findall('公司行业：(\w+)公司', str(h))[0]
                compyplace = re.findall('公司地址：(\w+)', str(h))[0]
                print(compyxingzhi, companyname, compynum, compyplace, whatwork)
                try:
                    compyurl = re.findall('公司主页：(.*?)公司', str(h))[0]
                    item['company_url'] = compyurl
                except:
                    item['company_url'] = ""
                    pass
                compyintroduce = ""
                item['company_name'] = companyname
                item['company_xin_zhi'] = compyxingzhi
                item['company_num'] = compynum
                item['what_work'] = whatwork
                item['company_place'] = compyplace
                item['company_introduce'] = compyintroduce
                print(item)
                yield item