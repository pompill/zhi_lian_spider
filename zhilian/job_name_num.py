import urllib.request as ur
import re
from bs4 import BeautifulSoup as bs
import redis
r = redis.Redis(host='localhost',port=6379,db=0)
def getreq(url):
    header={'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
            'Cookie':'guid = c17c - 320b - c059 - f9b1;key = c4746acf0aa8c8a139fae3a1a47fc9a0',}
    req = ur.Request(url, headers=header)
    html = ur.urlopen(req).read().decode('utf-8')
    return html
def getname_num(html):
    soup = bs(html,'html.parser')
    if soup.select('.search_bottom_content div h1 a'):
        item = soup.select('.search_bottom_content div h1 a')
        for i in item:
            jurl = i.get('href')
            jnum = re.search('bj=(\d+)&sj=(\d+)', jurl).group(0)
            r.sadd('jobnum',jnum)
if __name__=="__main__":
    url = "http://sou.zhaopin.com/"
    html = getreq(url)
    jnum = getname_num(html)
    print(jnum)
