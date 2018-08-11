# -- encoding:utf-8 --

import requests
from bs4 import BeautifulSoup
import pymongo
import datetime
import os


class ScrapingWeb():
    ''' 根据scraping_baidu的结果，提取网页中的全部正文。
        Args:
            url : 带提取的网页
            connection : mongo链接地址 
        Returns:
            将网页中的正文存入mongodb中
    '''
    __db_to_get = None  # mongo 数据库
    __url = []   # 保存url地址，为列表对象
    __fn = None  # 用于记录程序运行过程

    def __init__(self, **kwargs):
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if os.path.isfile('info.txt'):
            os.remove('info.txt')
        self.__fn = open('info.txt', 'a+')
        # 建立数据库连接
        try:
            if kwargs.__contains__('connection'):
                self.__db_to_get = pymongo.MongoClient(
                    host=kwargs['connection'])
            else:
                self.__db_to_get = pymongo.MongoClient(host=['localhost'],
                                                       port=27017)
        except pymongo.errors.ConnectionFailure:
            self.__fn.write('数据库: 连接错误！\n 连接时间: %s \n' % (str(time_now)))
            print('Server not available!')
        else:
            self.__fn.write('数据库连接成功!\n 连接时间: %s \n' % (str(time_now)))
            print('Mongo connection is successful!')
            doc = self.__db_to_get['search_baidu'].results.find({})
            self.__get_url(doc)
        finally:
            self.__fn.close()

    def Scraping_url(self):
        count = 0  # 计数器
        for url in self.__url[:5]:
            html = requests.get(url, timeout=5)
            print('网页响应状况: %d' % (html.status_code))
            doc = BeautifulSoup(html.text, 'lxml').select('p')
        print(len(doc))

    def __get_url(self, documents):
        # 从documents中提取url地址
        for doc in documents:
            self.__url.append(doc['href'])
        self.__url = list(set(self.__url))  # 去掉重复的url
        self.__fn.write('读取数据库中的href：共计 %d' % (len(self.__url)))
        self.__fn.close()


if __name__ == '__main__':
    #    connection = 'www.plusenplus.cn:27021'
    #    test = ScrapingWeb(connection=connection)
    test = ScrapingWeb()
    test.Scraping_url()
