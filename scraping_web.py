# -- encoding:utf-8 --

import request
from bs4 import BeautifulSoup
import pymongo
import datetime


class ScrapingWeb():
    ''' 根据scraping_baidu的结果，提取网页中的全部正文。
        Args:
            url : 带提取的网页
            db: mongo 数据库的地址
        Returns:
            将网页中的正文存入mongodb中
    '''
    db_to_get = None

    def __ini__(self, **kwargs):
        try:
            if kwargs.has_key('connection'):
                self.db_to_get = pymongo.MongoClient(host=kwargs['connection'])
            else:
                self.db_to_get = pymongo.MongoClient(
                        host=['localhost'],port=27017)
        except pymongo.errors.ConnectionFailure as e:
            with open('error.txt', 'w+') as fn:
                time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                fn.write(
                        '''数据库: 连接错误！\n 
                           连接时间: %s \n''' % (str(time_now)))
                fn.close()


