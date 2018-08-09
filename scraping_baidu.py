# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import pymongo
import time

# 定义爬虫类


class baidu_search():
    # 爬取baidu搜索的结果
    # kw: keyword
    # mpn: maximun of the pages number to search
    kw = None
    mpn = None
    iter_count = 0
    __deldatabase = True
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

    def __init__(self, kw, mpn,deldb = True):
        # 初始化变量
        self.kw = kw  # keyword to search
        self.mpn = mpn
        self.__deldatabase = deldb
       # 初始化网页
        try:
            # 建立mongodblian连接
            self.__db = pymongo.MongoClient('127.0.0.1', 27017)
            self.__db_table = self.__db.search_baidu  # 在mongodb中建立名为search_baidu数据库
            # 建立一个collection 用于保存搜索结果
            self.__collection = self.__db_table['results']
            if self.__deldatabase:
                self.__collection.delete_many({})
        except Exception:
            import traceback
            traceback.print_exc()
            fn = open('error.txt','+w')
            fn.write('error:MongoClient error!\n')
            fn.close()

    def scraping(self):
        maxpage = self.mpn
        fn = open('log.txt', "+w")
        fn.write("用于读取百度搜索结果\n")
        for i in range(maxpage):
            # building url to search
            url = self.__url.format(self.kw, i + 1)
            print(url)
            try:
                response = requests.get(url, headers=self.__headers)
                response.raise_for_status()  # 抛出异常
            except Exception:
                import traceback
                traceback.print_exc()
                fn.writelines(traceback.print_exc)
                break
            else:
                html = BeautifulSoup(response.text, 'lxml')
                time.sleep(1)
                self.scraping_html(html, i + 1)
                self.iter_count += 1
                fn.writelines("读取第 " + str(self.iter_count) + " 页\n")
        fn.write("抓取完毕！\n")
        fn.close()

    def scraping_html(self, html, ID):
        # 寻找内容
        div_container = html.select('div.c-container')
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
            results = {'title': str(title),
                       'href': str(href),
                       'abstract': str(abstract)
                       }
            self.__collection.update_one(
                {'_id': ID}, {'$set': results}, upsert=True)

    def print_querying(self):
        for x in self.__collection.find():
            print(x)
        print("\ncounting:", self.__collection.count())


if __name__ == '__main__':
    kw = 'title:(分享经济) “分享?企业”+“分享?模式”'
    kw = '分享经济'
    test = baidu_search(kw, 2)
    test.scraping()
    test.print_querying()
