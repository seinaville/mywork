# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery
import pymongo

# 定义爬虫类


class baidu_search():
    # 爬取baidu搜索的结果
    # kw: keyword
    # pn: page number
    # fn: file to store the search result
    __url = 'http://www.baidu.com/s?wd={}&pn={}'
    __headers = {
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-language': 'en-Us,en;q=0.7,zh-CN;q=0.4',
        'Host': 'www.baidu.com',
        'Cache-control': 'max-age=0',
        'Connection': 'Keep-alive',
        'User-Agent': 'Mozilla / 5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit / 537.36 (KHTML, like Gecko) Chrome / 68.0.3440.84 Safari / 537.36'
    }

    def __init__(self, kw, pn):
        # 初始化变量
        self.kw = kw  # keyword to search
        self.pn = pn
        # building url to search
        self.__url = self.__url.format(self.kw, self.pn)
        # 初始化网页
        try:
            self.__response = requests.get(self.__url, headers=self.__headers)
            self.__response.raise_for_status()  # 抛出异常
            self.__html = BeautifulSoup(self.__response.text, "lxml")
            # 建立mongodblian连接
            self.__db = pymongo.MongoClient('127.0.0.1', 27017)
            self.__db__table = self.__db.search_baidu  # 在mongodb中建立名为search_baidu数据库
            # 建立一个collection 用于保存搜索结果
            self.__collection = self.__db__table['results']
        except Exception:
            import traceback
            traceback.print_exc()

    def scraping_html(self):
        results = []
        # 寻找内容
        # doc = self.__html.find_all("div", class_='c-container')
        div_container = self.__html.select('div.c-container')
        for element in div_container:
            node = element.select("h3 a")  # 寻找title和href所在节点
            title = node[0].get_text()
            href = node[0].attrs['href']
            # 寻找同一级别的子类
            node_abstract = element.select('div.c-abstract')
            if len(node_abstract) == 1:
                abstract = node_abstract[0].get_text()
            else:
                abstract = None
            # 保存结果
            results.append({
                'title': str(title),
                'href': str(href),
                'abstract': str(abstract)
            })
       # print(results)
        # save results into mongodb
        # self.__collection.insert_many(results)
        self.__collection.update_many

    def print_querying(self):
        for x in self.__collection.find():
            print(x)
        print("\ncounting:", self.__collection.count())


if __name__ == '__main__':
    test = baidu_search('分享经济企业', 1)
    test.scraping_html()
    test.print_querying()
