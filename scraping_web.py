# -- encoding:utf-8 --

'''
todo:
    由于mongo远程链接有时间限制，需要予以解决
'''

import requests
from bs4 import BeautifulSoup
import pymongo
import datetime
import os
import chardet

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
    __header = {
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-language': 'en-Us,en;q=0.7,zh-CN;q=0.4',
        'Cache-control': 'max-age=0',
        'Connection': 'Keep-alive',
        'User-Agent': 'Mozilla / 5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit / 537.36 (KHTML, like Gecko) Chrome / 68.0.3440.84 Safari / 537.36'
    }

    def __init__(self, **kwargs):
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if os.path.isfile('info.txt'):
            os.remove('info.txt')
        # 建立数据库连接
        try:
            if kwargs.__contains__('connection'):
                self.__db_to_get = pymongo.MongoClient(
                    host=kwargs['connection'])
            else:
                self.__db_to_get = pymongo.MongoClient(host=['localhost'],
                                                       port=27017)
        except pymongo.errors.ConnectionFailure:
            self.__output_message('数据库: 连接错误！\n 连接时间: %s \n' % (str(time_now)))
            print('Server not available!')
        else:
            self.__output_message('数据库连接成功!\n 连接时间: %s \n' % (str(time_now)))
            print('Mongo connection is successful!')
            doc = self.__db_to_get['search_baidu'].results.find({})
            self.__get_url(doc)

    def Scraping_url(self):
        count = 0  # 计数器
        for url in self.__url[:100]:  # 读取网页地址
            try:
                html = requests.get(
                    url, headers=self.__header,
                    timeout=10, allow_redirects=True)  # 请求网页，3秒内响应
                html.raise_for_status()
                # 对网页编码进行检测
                encode = chardet.detect(html.content)['encoding']
                if 'GB' in encode:
                    html.encoding = 'GBK'
                    print(html.text)
            except requests.exceptions.RequestException:
                self.__output_message('网页: %s 请求异常\n网页响应状况: %d \n'
                                      % (url, html.status_code))
                print('=====================================\n')
                print('网页: %s 请求异常\n网页响应状况: %d \n' % (url,
                                                      html.status_code))
            else:
                # 读取网页内所有的节点<P>
                count += 1
                doc = BeautifulSoup(html.text, 'lxml').select('p')
                text = ''  # 初始化正文存储器
                for tag in doc:  # 合并正文
                    text = '%s ，%s' % (text, tag.get_text())
                self.__db_to_get['search_baidu'].mainbodytext.update_one(
                    {'_id': url},
                    {'$set': {'text': text}},
                    upsert=True)
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.__output_message('文字提取处理完毕: \n'
                              '\t共计处理: %d 页 \n'
                              '\t结果保存在"mainbodytext"集合.'
                              '程序结束时间: %s' % (count, str(time_now)))

    def __get_url(self, documents):
        # 从documents中提取url地址
        for doc in documents:
            self.__url.append(doc['href'])
        self.__url = list(set(self.__url))  # 去掉重复的url
        self.__output_message('读取数据库中的href：共计 %d \n' % (len(self.__url)))

    def __output_message(self, message):
        with open('info.txt', 'a+') as fn:
            fn.write(message)
            fn.close()


if __name__ == '__main__':
    #    connection = 'www.plusenplus.cn:27021'
    #    test = ScrapingWeb(connection=connection)
    test = ScrapingWeb()
    test.Scraping_url()
