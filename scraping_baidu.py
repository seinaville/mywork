# -*- coding:utf-8 -*-
import requests
import urllib
from bs4 import BeautifulSoup
import pymongo
import time
import random

# 定义爬虫类


class BaiduSearch():
    """ 爬取baidu搜索的结果
    通过关键词和设定最大搜索页数进行百度搜索结果爬虫

    args:
        kw: keyword
        mpn: maximun of the pages number to search
        deldb: a variable type booling, if true , the collection named 'results' that stored last
        data of scraping will be deleted

    Returns:
        A data base of type mongodb was created or updated and un txt objet named "log.txt" that will be
        created notes the status of programme processus during whole runing.
    """
    kw = None
    mpn = None
    __iter_count = 0  # 网页计数器
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

    def __init__(self, kw, mpn, deldb=True):
        """初始化变量"""
        self.kw = kw
        self.mpn = mpn
        self.__deldatabase = deldb
       # 初始化网页
        try:
            # 建立mongodblian连接
            self.__db = pymongo.MongoClient('127.0.0.1', 27017)
            self.__db_table = self.__db.search_baidu  # 在mongodb中建立名为search_baidu数据库
            # 建立一个collection 用于保存搜索结果
            self.__collection = self.__db_table['search_url']
            if self.__deldatabase:  # 判断是否删除旧的数据
                self.__collection.delete_many({})
        except Exception:
            import traceback
            traceback.print_exc()
            fn = open("error.txt", "w")
            fn.write('error:MongoClient error!\n')
            fn.close()

    def scraping(self):
        """ 通过建立搜索网页地址，以最大网页数mpx为上限，进行循环爬取"""
        maxpage = self.mpn
        fn = open("log.txt", "w")
        fn.write('用于读取百度搜索结果\n')
        for i in range(maxpage):
            # building url to search
            url = self.__url.format(self.kw, i + 1)
            try:
                response = requests.get(url, headers=self.__headers)
                response.raise_for_status()  # 抛出异常
            except Exception:
                import traceback
                fn.writelines(traceback.print_exc)
            else:
                html = BeautifulSoup(response.text, 'lxml')  # 解析网页
                time.sleep(random.random() * 3)  # 设定每次爬虫的时间间隔
                self.scraping_html(html, i + 1)
                self.__iter_count += 1
                # 每爬取10个网页进行一次程序进程记录并输出到log.txt文件中
                if self.__iter_count % 10 == 0:
                    fn.write('读取第 %d 页\n' % (self.__iter_count))
        fn.write('程序运行结束，恭喜！')
        fn.close()

    def scraping_html(self, html, ID):
        """scraping_html 函数接收html和ID(当前页数)两个参数，对html进行内容搜索并将结果保存到
        mongodb中的search_baidu基础数据库中，数据集'_id'为当前数据个数"""

        db_id = (ID - 1) * 10 + 1  # 数据计数
        # 搜索title, href和absctract的父节点
        div_container = html.select('div.c-container')
        for element in div_container:
            node = element.select("h3 a")  # 寻找title和href所在节点
            title = node[0].get_text(strip=True)
            href = node[0].attrs['href']
            node_abstract = element.select('div.c-abstract')  # 寻找abstract所在的节点
            """ 判断abstract节点是否存在。如果存在予以计入，否则记录为None """
            if len(node_abstract) == 1:
                abstract = node_abstract[0].get_text(strip=True)
            else:
                abstract = None
            # 保存结果
            results = {
                'title': title,  # 去掉 \xa0 空格问题
                'href': str(href),
                'abstract': abstract
            }
            self.__collection.update_one(
                filter={'_id': db_id},
                update={'$set': results},
                upsert=True
            )
            db_id += 1

    def print_querying(self):
        for x in self.__collection.find():
            print(x)
        print("\ncounting:", self.__collection.count())


if __name__ == '__main__':
    kw = 'title:(分享经济)'
    test = BaiduSearch(kw, 10000)
    test.scraping()
