# -- encoding:utf-8 --

import requests
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
    __db_to_get = None

    def __init__(self, **kwargs):
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fn = open('error.txt', 'w+')
        try:
            if kwargs.__contains__('connection'):
                self.__db_to_get = pymongo.MongoClient(
                    host=kwargs['connection'])
            else:
                self.__db_to_get = pymongo.MongoClient(host=['localhost'],
                                                       port=27017)
        except pymongo.errors.ConnectionFailure:
            fn.write('数据库: 连接错误！\n 连接时间: %s \n' % (str(time_now)))
            print('Server not available!')
        else:
            fn.write('数据库连接成功!\n 连接时间: %s \n' % (str(time_now)))
            print('Mongo connection is successful!')


if __name__ == '__main__':
    connection = 'www.plusenplus.cn:27021'
    test = ScrapingWeb(connection=connection)
